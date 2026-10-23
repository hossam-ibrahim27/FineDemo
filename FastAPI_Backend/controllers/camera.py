import threading
import time
from collections import defaultdict
from datetime import datetime
import cv2
from helpers.config import (
    CONFIDENCE, DEFAULT_VIDEO, DEFECT_LABEL, DEVICE, FRAME_SIZE, GOOD_LABEL,
    LOST_FRAMES, MIN_BOX_AREA_RATIO, MIN_VOTES_ON_EXIT, VOTES_REQUIRED,
)

class CameraStreamManager:
    def __init__(self, camera_id: str, model, db,
                 arduino=None, video_source: str = DEFAULT_VIDEO):
        self.camera_id = camera_id
        self.video_source = video_source
        self.model = model
        self.db = db
        self.arduino = arduino

        # GET CLASS IDS FOR GOOD AND DEFECTIVE FROM MODEL (SAME AS ANNOTATION)
        self.good_id, self.defect_id = self._resolve_class_ids()

        self.is_running = False
        self.cap = None
        self.lock = threading.RLock()   # RLock: the same thread may take it again

        self.votes = defaultdict(list)  # track_id -> [True if defective, ...]
        self.last_seen = {}             # track_id -> frame number it was last detected
        self.frame_idx = 0
        self.processed_ids = set()
        self.pass_count = 0
        self.reject_count = 0
        self.live_session_logs = []     # what the UI shows for the current session
        self._unsaved = []              # rows waiting to be written to MySQL on stop

    # ---------- Setup ----------
    def _resolve_class_ids(self):
        names = self.model.names
        items = names.items() if isinstance(names, dict) else enumerate(names)
        class_names = {int(k): str(v).strip().lower() for k, v in items}
        print("[INFO] Classes:", class_names)

        good = [k for k, v in class_names.items() if v == GOOD_LABEL]
        defect = [k for k, v in class_names.items() if v == DEFECT_LABEL]
        if not good or not defect:
            raise ValueError(
                f"Expected classes '{GOOD_LABEL}' and '{DEFECT_LABEL}'. Found: {class_names}"
            )
        return good[0], defect[0]

    def _reset_tracking(self):
        self.votes.clear()
        self.last_seen.clear()
        self.processed_ids.clear()

    def _reset_session(self):
        self._reset_tracking()
        self.live_session_logs.clear()
        self.pass_count = 0
        self.reject_count = 0

    # ---------- Control ----------
    def start_monitoring(self):
        with self.lock:
            if self.is_running:
                return {"status": "info", "message": f"Camera {self.camera_id} is already running."}
            self._reset_session()
            if self.cap is None or not self.cap.isOpened():
                self.cap = cv2.VideoCapture(self.video_source)
            self.is_running = True
            return {"status": "success", "message": f"Camera {self.camera_id} started monitoring."}

    def stop_monitoring(self):
            with self.lock:
                self.is_running = False
                unsaved, self._unsaved = self._unsaved, []
    
            if self.arduino:
                self.arduino.send("X")   # relay OFF
    
            saved = 0
            if unsaved:
                print(f"[STOP] saving {len(unsaved)} defects to the database...")
                try:
                    saved = self.db.log_many(unsaved)   # history is written ONLY here
                    print(f"[STOP] saved {saved} rows")
                except Exception as e:
                    print(f"[DB Error]: {type(e).__name__}: {e}")
                    with self.lock:
                        self._unsaved = unsaved + self._unsaved
                    return {
                        "status": "warning",
                        "message": f"Camera {self.camera_id} stopped, but saving to the database failed.",
                        "saved": 0,
                        "error": str(e),
                    }
            else:
                print("[STOP] nothing to save")
            return {
                "status": "success",
                "message": f"Camera {self.camera_id} stopped monitoring.",
                "saved": saved,
            }
    def get_stats(self):
        return {
            "total_tracked_packages": self.pass_count + self.reject_count,
            "defective_packages": self.reject_count,
            "system_status": "Active Mode" if self.is_running else "Standby Mode",
            "is_running": self.is_running,
        }

    # ---------- Streaming ----------
    def generate_frames(self):
        while True:
            if self.cap is None or not self.cap.isOpened():
                self.cap = cv2.VideoCapture(self.video_source)
                if not self.cap.isOpened():
                    time.sleep(0.5)
                    continue

            ok, frame = self.cap.read()
            if not ok:
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                with self.lock:
                    self._reset_tracking()
                continue

            output = self._inspect(frame) if self.is_running else frame
            output = cv2.resize(output, FRAME_SIZE)

            _, buffer = cv2.imencode(".jpg", output)
            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n" + buffer.tobytes() + b"\r\n"
            )
            time.sleep(0.03)

    # ---------- Inference + voting ----------
    def _inspect(self, frame):
        result = self.model.track(
            frame,
            persist=True,
            tracker="bytetrack.yaml",
            conf=CONFIDENCE,
            verbose=False,
            device=DEVICE,
        )[0]

        ids, classes, areas, min_area = [], [], [], 0.0
        boxes = result.boxes
        if boxes is not None and boxes.id is not None and boxes.cls is not None:
            height, width = frame.shape[:2]
            min_area = MIN_BOX_AREA_RATIO * width * height
            ids = boxes.id.int().cpu().tolist()
            classes = boxes.cls.int().cpu().tolist()
            areas = (boxes.xywh[:, 2] * boxes.xywh[:, 3]).cpu().tolist()

        with self.lock:
            if self.is_running:   # a frame that finishes after Stop must not vote
                self.frame_idx += 1
                for track_id, class_id, area in zip(ids, classes, areas):
                    self.last_seen[track_id] = self.frame_idx
                    if area >= min_area:   # far / tiny boxes are unreliable: no vote
                        self._vote(track_id, class_id)
                self._flush_lost_tracks()

        return result.plot()

    def _vote(self, track_id: int, class_id: int):
        if track_id in self.processed_ids:
            return
        if class_id not in (self.good_id, self.defect_id):
            return

        history = self.votes[track_id]
        history.append(class_id == self.defect_id)   # True = defective
        if len(history) >= VOTES_REQUIRED:
            self._decide(track_id)

    def _flush_lost_tracks(self):
        """A package that left the frame before collecting enough votes is decided
        with the votes it has, instead of being skipped."""
        lost = [t for t, seen in self.last_seen.items()
                if self.frame_idx - seen > LOST_FRAMES]
        for track_id in lost:
            del self.last_seen[track_id]
            if track_id in self.processed_ids:
                continue
            if len(self.votes.get(track_id, [])) >= MIN_VOTES_ON_EXIT:
                self._decide(track_id)
            else:
                self.votes.pop(track_id, None)

    def _decide(self, track_id: int):
        history = self.votes.pop(track_id, [])
        self.processed_ids.add(track_id)
        defect_votes = sum(history)
        is_defective = defect_votes * 2 >= len(history)   # majority, a tie rejects

        if is_defective:
            self.reject_count += 1
            print(f"[DECISION] ID {track_id}: DEFECTIVE ({defect_votes}/{len(history)} votes)")
            if self.arduino:
                self.arduino.send("R")
            self._record_defect(track_id)
        else:
            self.pass_count += 1
            print(f"[DECISION] ID {track_id}: GOOD - PASS ({defect_votes}/{len(history)} defective votes)")

        print(f"[COUNT] PASS={self.pass_count}, REJECT={self.reject_count}")

    def _record_defect(self, track_id: int):
        stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self.lock:
            self.live_session_logs.insert(0, {
                "Camera": f"CAM #{self.camera_id}",
                "Track ID": track_id,
                "defective": "defective",
                "Time": stamp,
            })
        self._unsaved.append((track_id, True, stamp))   # saved on stop