from contextlib import asynccontextmanager
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import os
import threading
import time

import cv2
import serial
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from ultralytics import YOLO

from Database import DatabaseHandler


# =====================================================
# 1. Environment Configuration
# =====================================================

load_dotenv(dotenv_path="assets/.env")


# =====================================================
# 2. Database: Optional for Temporary Testing
# =====================================================

db = None

try:
    db = DatabaseHandler(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "vision_db"),
        port=int(os.getenv("DB_PORT", 3306)),
    )

    print("MySQL connected successfully!")

except Exception as e:
    print(f"MySQL unavailable: {e}")
    print("Continuing without database...")


# =====================================================
# 3. Load YOLO Model
# =====================================================

yolo_tracker = YOLO("model/best.pt")

executor = ThreadPoolExecutor(max_workers=4)


# =====================================================
# 4. Arduino Configuration
# =====================================================

ARDUINO_PORT = "COM6"
ARDUINO_BAUDRATE = 9600

arduino = None
arduino_lock = threading.Lock()


def connect_arduino():
    """
    Connect to Arduino when the FastAPI application starts.
    """

    global arduino

    try:
        with arduino_lock:
            if arduino is not None and arduino.is_open:
                return

            arduino = serial.Serial(
                port=ARDUINO_PORT,
                baudrate=ARDUINO_BAUDRATE,
                timeout=1,
            )

        # Arduino Uno may reset when the serial port opens.
        time.sleep(2)

        print(f"Arduino connected successfully on {ARDUINO_PORT}")

    except (serial.SerialException, OSError) as e:
        arduino = None
        print(f"Arduino connection failed: {e}")
        print("AI can still run without Arduino.")


def send_arduino_command(command: str):
    """
    Send ON or OFF to Arduino.
    The Arduino sketch must recognize these commands.
    """

    global arduino

    if command not in ("ON", "OFF"):
        print(f"Invalid Arduino command: {command}")
        return

    try:
        with arduino_lock:
            if arduino is None or not arduino.is_open:
                print("Arduino is not connected.")
                return

            arduino.write((command + "\n").encode("utf-8"))
            arduino.flush()

        print(f"Arduino command sent: {command}")

    except (serial.SerialException, OSError) as e:
        print(f"Arduino communication error: {e}")


def close_arduino():
    """
    Turn off the LED and close the serial connection.
    """

    global arduino

    try:
        with arduino_lock:
            if arduino is not None and arduino.is_open:
                arduino.write(b"OFF\n")
                arduino.flush()
                arduino.close()

        arduino = None
        print("Arduino connection closed.")

    except (serial.SerialException, OSError) as e:
        print(f"Error closing Arduino: {e}")


# =====================================================
# 5. Camera / Video Stream Manager
# =====================================================

CY_LINE = 360
OFFSET = 35

ROI_X_MIN = 200
ROI_X_MAX = 800


class CameraStreamManager:

    def __init__(
        self,
        camera_id: str,
        video_source: str = "videos/fineDemo.mp4",
    ):
        self.camera_id = camera_id
        self.video_source = video_source

        self.is_running = False
        self.cap = None

        self.lock = threading.Lock()

        self.total_tracked = 0
        self.defective_count = 0

        self.processed_ids = set()
        self.live_session_logs = []

    def start_monitoring(self):

        with self.lock:

            if self.is_running:
                return {
                    "status": "info",
                    "message": (
                        f"Camera {self.camera_id} "
                        "is already running."
                    ),
                }

            self.processed_ids.clear()
            self.live_session_logs.clear()

            self.total_tracked = 0
            self.defective_count = 0

            if self.cap is None or not self.cap.isOpened():

                self.cap = cv2.VideoCapture(
                    self.video_source
                )

            if not self.cap.isOpened():

                return {
                    "status": "error",
                    "message": (
                        f"Could not open video: "
                        f"{self.video_source}"
                    ),
                }

            # Start video from the beginning.
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

            self.is_running = True

            # Reset the Arduino LED before a new session.
            send_arduino_command("OFF")

            return {
                "status": "success",
                "message": (
                    f"Camera {self.camera_id} "
                    "started monitoring."
                ),
            }

    def stop_monitoring(self):

        with self.lock:
            self.is_running = False

        # Turn the LED off when monitoring stops.
        send_arduino_command("OFF")

        return {
            "status": "success",
            "message": (
                f"Camera {self.camera_id} "
                "stopped monitoring."
            ),
        }

    def get_stats(self):

        return {
            "total_tracked_packages": self.total_tracked,
            "defective_packages": self.defective_count,
            "system_status": (
                "Active Mode"
                if self.is_running
                else "Standby Mode"
            ),
            "is_running": self.is_running,
        }

    def generate_frames(self):

        if self.cap is None or not self.cap.isOpened():

            self.cap = cv2.VideoCapture(
                self.video_source
            )

        while True:

            if self.cap is None or not self.cap.isOpened():

                time.sleep(0.2)
                continue

            ret, frame = self.cap.read()

            if not ret:

                # Restart the video after reaching the end.
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

                # Allow IDs to be counted again on replay.
                self.processed_ids.clear()

                continue

            resized_frame = cv2.resize(
                frame,
                (1020, 500),
            )

            cv2.line(
                resized_frame,
                (0, CY_LINE),
                (1020, CY_LINE),
                (0, 255, 255),
                2,
            )

            if self.is_running:

                results = yolo_tracker.track(
                    resized_frame,
                    persist=True,
                    verbose=False,
                    device="cpu",
                )

                if (
                    results
                    and results[0].boxes is not None
                    and results[0].boxes.id is not None
                ):

                    boxes = (
                        results[0]
                        .boxes.xyxy.int()
                        .cpu()
                        .tolist()
                    )

                    track_ids = (
                        results[0]
                        .boxes.id.int()
                        .cpu()
                        .tolist()
                    )

                    cls_ids = (
                        results[0]
                        .boxes.cls.int()
                        .cpu()
                        .tolist()
                        if results[0].boxes.cls is not None
                        else []
                    )

                    for idx, (box, track_id) in enumerate(
                        zip(boxes, track_ids)
                    ):

                        x1, y1, x2, y2 = box

                        cx = (x1 + x2) // 2
                        cy = (y1 + y2) // 2

                        # Ignore detections outside the ROI.
                        if cx < ROI_X_MIN or cx > ROI_X_MAX:
                            continue

                        cls_id = (
                            cls_ids[idx]
                            if idx < len(cls_ids)
                            else None
                        )

                        # Assumption from the existing project:
                        # class 0 = defective product.
                        is_damaged = cls_id == 0

                        box_color = (
                            (0, 0, 255)
                            if is_damaged
                            else (0, 255, 0)
                        )

                        status_text = (
                            f"ID: {track_id} "
                            f"{'[DAMAGED]' if is_damaged else '[NORMAL]'}"
                        )

                        cv2.rectangle(
                            resized_frame,
                            (x1, y1),
                            (x2, y2),
                            box_color,
                            2,
                        )

                        cv2.putText(
                            resized_frame,
                            status_text,
                            (x1, max(y1 - 10, 20)),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.5,
                            box_color,
                            2,
                        )

                        crossed_line = (
                            CY_LINE - OFFSET
                            <= cy
                            <= CY_LINE + OFFSET
                        ) or (
                            CY_LINE - OFFSET
                            <= y2
                            <= CY_LINE + OFFSET
                        )

                        if (
                            crossed_line
                            and track_id not in self.processed_ids
                        ):

                            self.processed_ids.add(track_id)

                            with self.lock:
                                self.total_tracked += 1

                            h, w, _ = resized_frame.shape

                            crop_x1 = max(0, x1)
                            crop_y1 = max(0, y1)

                            crop_x2 = min(w, x2)
                            crop_y2 = min(h, y2)

                            crop = resized_frame[
                                crop_y1:crop_y2,
                                crop_x1:crop_x2,
                            ].copy()

                            if crop.size > 0:

                                executor.submit(
                                    self._process_detection,
                                    crop,
                                    track_id,
                                    cls_id,
                                )

            success, buffer = cv2.imencode(
                ".jpg",
                resized_frame,
            )

            if success:

                frame_bytes = buffer.tobytes()

                yield (
                    b"--frame\r\n"
                    b"Content-Type: image/jpeg\r\n\r\n"
                    + frame_bytes
                    + b"\r\n"
                )

            time.sleep(0.03)

    def _process_detection(
        self,
        crop,
        track_id,
        cls_id=None,
    ):

        # Use the existing YOLO detection result.
        damage_status = cls_id == 0 if cls_id is not None else False

        if damage_status:

            with self.lock:
                self.defective_count += 1

                timestamp_str = datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                )

                log_entry = {
                    "Camera": f"CAM #{self.camera_id}",
                    "Track ID": track_id,
                    "damage": "Damaged",
                    "Time": timestamp_str,
                }

                self.live_session_logs.insert(
                    0,
                    log_entry,
                )

            # Signal Arduino when a defective product is detected.
            # The LED remains ON until OFF is sent.
            send_arduino_command("ON")

            # Save to MySQL only when the connection is available.
            if db is not None:

                try:
                    db.log_inspection(
                        track_id=track_id,
                        damage=True,
                    )

                except Exception as e:
                    print(f"[DB Error]: {e}")


# =====================================================
# 6. Create Camera Manager
# =====================================================

cameras = {
    "1": CameraStreamManager(
        camera_id="1",
        video_source="videos/fineDemo.mp4",
    )
}

print("Model Classes:", yolo_tracker.names)


# =====================================================
# 7. FastAPI Lifespan
# =====================================================

@asynccontextmanager
async def lifespan(app: FastAPI):

    print("Starting InspectVision API...")

    connect_arduino()

    yield

    print("Stopping InspectVision API...")

    for camera in cameras.values():

        camera.stop_monitoring()

        if camera.cap is not None:
            camera.cap.release()
            camera.cap = None

    close_arduino()

    executor.shutdown(wait=False)

    if db is not None and hasattr(db, "close"):

        try:
            db.close()

        except Exception as e:
            print(f"[DB Close Error]: {e}")


# =====================================================
# 8. FastAPI Application
# =====================================================

app = FastAPI(
    title="InspectVision API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =====================================================
# 9. API Endpoints
# =====================================================

@app.get("/")
def home():

    return {
        "message": "InspectVision API is running",
        "database_connected": db is not None,
        "arduino_port": ARDUINO_PORT,
        "model_classes": yolo_tracker.names,
    }


@app.get("/api/v1/{cam_id}/feed")
def video_feed(cam_id: str):

    if cam_id not in cameras:
        raise HTTPException(
            status_code=404,
            detail="Camera not found",
        )

    return StreamingResponse(
        cameras[cam_id].generate_frames(),
        media_type="multipart/x-mixed-replace; boundary=frame",
    )


@app.post("/api/v1/{cam_id}/start")
def start_camera(cam_id: str):

    if cam_id not in cameras:
        raise HTTPException(
            status_code=404,
            detail="Camera not found",
        )

    return cameras[cam_id].start_monitoring()


@app.post("/api/v1/{cam_id}/stop")
def stop_camera(cam_id: str):

    if cam_id not in cameras:
        raise HTTPException(
            status_code=404,
            detail="Camera not found",
        )

    return cameras[cam_id].stop_monitoring()


@app.get("/api/v1/{cam_id}/stats")
def camera_stats(cam_id: str):

    if cam_id not in cameras:
        raise HTTPException(
            status_code=404,
            detail="Camera not found",
        )

    return cameras[cam_id].get_stats()


@app.get("/api/v1/{cam_id}/live_session_logs")
def live_session_logs(cam_id: str):

    if cam_id not in cameras:
        raise HTTPException(
            status_code=404,
            detail="Camera not found",
        )

    with cameras[cam_id].lock:
        return cameras[cam_id].live_session_logs


@app.get("/api/history_logs")
def history_logs():

    if db is None:
        return []

    try:
        return db.get_all_logs()

    except Exception as e:
        print(f"[DB Error]: {e}")

        return []