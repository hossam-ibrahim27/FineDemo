import threading
import time
from datetime import datetime

import cv2

from helpers.config import (
    CY_LINE, OFFSET, ROI_X_MIN, ROI_X_MAX, FRAME_SIZE, DEFAULT_VIDEO,
)


class CameraStreamManager:
    def __init__(self, camera_id: str, model, db, executor,
                 video_source: str = DEFAULT_VIDEO):
        self.camera_id = camera_id
        self.video_source = video_source
        self.model = model
        self.db = db
        self.executor = executor

        self.is_running = False
        self.cap = None
        self.lock = threading.Lock()

        # Stats and session logs
        self.total_tracked = 0
        self.defective_count = 0
        self.processed_ids = set()
        self.live_session_logs = []

    # ---------- Control ----------
    def start_monitoring(self):
        with self.lock:
            if not self.is_running:
                self.processed_ids.clear()
                self.live_session_logs.clear()
                self.total_tracked = 0
                self.defective_count = 0

                if self.cap is None or not self.cap.isOpened():
                    self.cap = cv2.VideoCapture(self.video_source)
                self.is_running = True
                return {"status": "success", "message": f"Camera {self.camera_id} started monitoring."}
            return {"status": "info", "message": f"Camera {self.camera_id} is already running."}

    def stop_monitoring(self):
        with self.lock:
            self.is_running = False
            return {"status": "success", "message": f"Camera {self.camera_id} stopped monitoring."}

    def get_stats(self):
        return {
            "total_tracked_packages": self.total_tracked,
            "defective_packages": self.defective_count,
            "system_status": "Active Mode" if self.is_running else "Standby Mode",
            "is_running": self.is_running,
        }

    # ---------- Streaming ----------
    def generate_frames(self):
        if self.cap is None or not self.cap.isOpened():
            self.cap = cv2.VideoCapture(self.video_source)

        while True:
            if not self.cap or not self.cap.isOpened():
                self.cap = cv2.VideoCapture(self.video_source)

            ret, frame = self.cap.read()
            if not ret:
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                self.processed_ids.clear()
                continue

            frame = cv2.resize(frame, FRAME_SIZE)
            cv2.line(frame, (0, CY_LINE), (FRAME_SIZE[0], CY_LINE), (0, 255, 255), 2)

            if self.is_running:
                self._track_and_draw(frame)

            _, buffer = cv2.imencode(".jpg", frame)
            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n" + buffer.tobytes() + b"\r\n"
            )
            time.sleep(0.03)

    def _track_and_draw(self, frame):
        results = self.model.track(frame, persist=True, verbose=False, device="cpu")
        boxes_obj = results[0].boxes
        if boxes_obj is None or boxes_obj.id is None:
            return

        boxes = boxes_obj.xyxy.int().cpu().tolist()
        track_ids = boxes_obj.id.int().cpu().tolist()
        cls_ids = boxes_obj.cls.int().cpu().tolist() if boxes_obj.cls is not None else []
        h, w, _ = frame.shape

        for idx, (box, track_id) in enumerate(zip(boxes, track_ids)):
            x1, y1, x2, y2 = box
            cx = (x1 + x2) // 2
            cy = (y1 + y2) // 2

            if cx < ROI_X_MIN or cx > ROI_X_MAX:
                continue

            cls_id = cls_ids[idx] if idx < len(cls_ids) else None
            is_damaged = cls_id == 0
            color = (0, 0, 255) if is_damaged else (0, 255, 0)
            label = f"ID: {track_id} {'[DAMAGED]' if is_damaged else '[NORMAL]'}"

            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame, label, (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

            crossed = (
                (CY_LINE - OFFSET) <= cy <= (CY_LINE + OFFSET)
                or (CY_LINE - OFFSET) <= y2 <= (CY_LINE + OFFSET)
            )
            if crossed and track_id not in self.processed_ids:
                self.processed_ids.add(track_id)
                self.total_tracked += 1

                crop = frame[max(0, y1):min(h, y2), max(0, x1):min(w, x2)].copy()
                if crop.size > 0:
                    self.executor.submit(self._process_detection, crop, track_id, cls_id)

    # ---------- Background processing ----------
    def _process_detection(self, crop, track_id, cls_id=None):
        damage_status = False

        if cls_id is not None:
            damage_status = cls_id == 0
        else:
            res = self.model.predict(crop, verbose=False)
            if res and res[0].boxes is not None and len(res[0].boxes) > 0:
                damage_status = any(c == 0 for c in res[0].boxes.cls.int().tolist())

        if not damage_status:
            return

        self.defective_count += 1
        self.live_session_logs.insert(0, {
            "Camera": f"CAM #{self.camera_id}",
            "Track ID": track_id,
            "damage": "Damaged",
            "Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        })

        try:
            self.db.log_inspection(track_id=track_id, damage=True)
        except Exception as e:
            print(f"[DB Error]: {e}")