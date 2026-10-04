from contextlib import asynccontextmanager
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import os
import threading
import time
import cv2
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from Database import DatabaseHandler
from ultralytics import YOLO

# ==========================================
# 1. SETUP & CONFIGURATION
# ==========================================
load_dotenv(dotenv_path="assets/.env")

# Database Connection
db = DatabaseHandler(
    host=os.getenv("DB_HOST", "localhost"),
    user=os.getenv("DB_USER", "root"),
    password=os.getenv("DB_PASSWORD", ""),
    database=os.getenv("DB_NAME", "vision_db"),
    port=int(os.getenv("DB_PORT", 3306)),
)

# YOLO Models Setup
yolo_tracker = YOLO("model/best.pt")

executor = ThreadPoolExecutor(max_workers=4)
CY_LINE = 380       
OFFSET = 15         
MIN_BOX_AREA = 8000
# ==========================================
# 2. CAMERA & STREAMING MANAGER CLASS
# ==========================================
class CameraStreamManager:
    def __init__(self, camera_id: str, video_source: str = "videos/fineDemo.mp4"):
        self.camera_id = camera_id
        self.video_source = video_source
        self.is_running = False
        self.cap = None
        self.lock = threading.Lock()
        
        # Stats and Session Logs
        self.total_tracked = 0
        self.defective_count = 0
        self.processed_ids = set()
        self.live_session_logs = []

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
            "is_running": self.is_running
        }

    def generate_frames(self):
        if self.cap is None or not self.cap.isOpened():
            self.cap = cv2.VideoCapture(self.video_source)

        CY_LINE = 360       
        OFFSET = 35         
        ROI_X_MIN = 200     
        ROI_X_MAX = 800  

        while True:
            if not self.cap or not self.cap.isOpened():
                self.cap = cv2.VideoCapture(self.video_source)

            ret, frame = self.cap.read()
            if not ret:
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                self.processed_ids.clear() 
                continue

            resized_frame = cv2.resize(frame, (1020, 500))

            cv2.line(
                resized_frame, (0, CY_LINE), (1020, CY_LINE), (0, 255, 255), 2
            )

            if self.is_running:
                results = yolo_tracker.track(
                    resized_frame, persist=True, verbose=False, device="cpu"
                )

                if (
                    results[0].boxes is not None
                    and results[0].boxes.id is not None
                ):
                    boxes = results[0].boxes.xyxy.int().cpu().tolist()
                    track_ids = results[0].boxes.id.int().cpu().tolist()
                    cls_ids = (
                        results[0].boxes.cls.int().cpu().tolist()
                        if results[0].boxes.cls is not None
                        else []
                    )

                    for idx, (box, track_id) in enumerate(zip(boxes, track_ids)):
                        x1, y1, x2, y2 = box
                        
                        cx = (x1 + x2) // 2
                        cy = (y1 + y2) // 2

                        if cx < ROI_X_MIN or cx > ROI_X_MAX:
                            continue

                        cls_id = cls_ids[idx] if idx < len(cls_ids) else None

                        is_damaged = (cls_id == 0)
                        box_color = (0, 0, 255) if is_damaged else (0, 255, 0)  
                        status_text = f"ID: {track_id} {'[DAMAGED]' if is_damaged else '[NORMAL]'}"

                        cv2.rectangle(
                            resized_frame, (x1, y1), (x2, y2), box_color, 2
                        )
                        cv2.putText(
                            resized_frame,
                            status_text,
                            (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.5,
                            box_color,
                            2,
                        )

                        if (CY_LINE - OFFSET) <= cy <= (CY_LINE + OFFSET) or (CY_LINE - OFFSET) <= y2 <= (CY_LINE + OFFSET):
                            if track_id not in self.processed_ids:
                                self.processed_ids.add(track_id)
                                self.total_tracked += 1  

                                h, w, _ = resized_frame.shape
                                crop_x1, crop_y1 = max(0, x1), max(0, y1)
                                crop_x2, crop_y2 = min(w, x2), min(h, y2)
                                crop = resized_frame[crop_y1:crop_y2, crop_x1:crop_x2].copy()

                                if crop.size > 0:
                                    executor.submit(
                                        self._process_detection, crop, track_id, cls_id
                                    )

            _, buffer = cv2.imencode(".jpg", resized_frame)
            frame_bytes = buffer.tobytes()

            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n"
            )
            
            time.sleep(0.03)
            
    def _process_detection(self, crop, track_id, cls_id=None):
        damage_status = False

        if cls_id is not None:
            damage_status = (cls_id == 0)
        else:
            defect_results = yolo_tracker.predict(crop, verbose=False)
            if defect_results and defect_results[0].boxes is not None and len(defect_results[0].boxes) > 0:
                for box_cls in defect_results[0].boxes.cls.int().tolist():
                    if box_cls == 0: 
                        damage_status = True
                        break

        if damage_status:
            self.defective_count += 1

            timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            log_entry = {
                "Camera": f"CAM #{self.camera_id}",
                "Track ID": track_id,
                "damage": "Damaged",
                "Time": timestamp_str,
            }

            self.live_session_logs.insert(0, log_entry)

            try:
                db.log_inspection(
                    track_id=track_id,
                    damage=True,
                )
            except Exception as e:
                print(f"[DB Error]: {e}")


# ==========================================
# 3. FASTAPI APP & CORS SETUP
# ==========================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    executor.shutdown(wait=False)
    if hasattr(db, 'close'):
        db.close()

app = FastAPI(title="InspectVision API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

cameras = {"1": CameraStreamManager(camera_id="1", video_source="videos/fineDemo.mp4")}

print("Model Classes:", yolo_tracker.names)

# ==========================================
# 4. API ENDPOINTS
# ==========================================
@app.get("/")
def root():
    return {"status": "Online", "system": "InspectVision Core System"}


@app.get("/api/v1/{cam_id}/feed")
def get_camera_feed(cam_id: str):
    if cam_id not in cameras:
        raise HTTPException(status_code=404, detail="Camera not found")
    return StreamingResponse(
        cameras[cam_id].generate_frames(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )


@app.post("/api/v1/{cam_id}/start")
def start_camera_monitoring(cam_id: str):
    if cam_id not in cameras:
        raise HTTPException(status_code=404, detail="Camera not found")
    return cameras[cam_id].start_monitoring()


@app.post("/api/v1/{cam_id}/stop")
def stop_camera_monitoring(cam_id: str):
    if cam_id not in cameras:
        raise HTTPException(status_code=404, detail="Camera not found")
    return cameras[cam_id].stop_monitoring()


@app.get("/api/v1/{cam_id}/stats")
def get_camera_stats(cam_id: str):
    if cam_id not in cameras:
        raise HTTPException(status_code=404, detail="Camera not found")
    return cameras[cam_id].get_stats()


@app.get("/api/v1/{cam_id}/live_session_logs")
def get_camera_live_logs(cam_id: str):
    if cam_id not in cameras:
        raise HTTPException(status_code=404, detail="Camera not found")
    return cameras[cam_id].live_session_logs


@app.get("/api/history_logs")
def get_history_logs():
    try:
        logs = db.get_all_logs()
        formatted_logs = []
        for log in logs:
            formatted_logs.append({
                "Camera": "CAM #1",
                "Track ID": log.get("track_id"),
                "damage": "Damaged" if log.get("damage") else "Normal",
                "Time": str(log.get("created_at", ""))
            })
        return formatted_logs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))