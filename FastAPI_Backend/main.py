from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from ultralytics import YOLO
from controllers.camera import CameraStreamManager
from helpers import config
from helpers.arduino import ArduinoHandler        
from helpers.mysql_db import DatabaseHandler
from routes.base import base_router
from routes.data import historyLogs_router
from routes.detect import detect_router
import torch

print('PyTorch:', torch.__version__)
print('CUDA available:', torch.cuda.is_available())
if torch.cuda.is_available():
    print('GPU:', torch.cuda.get_device_name(0))
print('GPU test passed!')

@asynccontextmanager
async def lifespan(app: FastAPI):
    # ---- startup ----
    app.state.db = DatabaseHandler(
        host=config.DB_HOST,
        user=config.DB_USER,
        password=config.DB_PASSWORD,
        database=config.DB_NAME,
        port=config.DB_PORT,
    )
    
    app.state.arduino = ArduinoHandler(config.ARDUINO_PORT, config.ARDUINO_BAUDRATE)
    app.state.arduino.connect()

    app.state.model = YOLO(config.MODEL_PATH)
    app.state.cameras = {
        "1": CameraStreamManager(
            camera_id="1",
            model=app.state.model,
            db=app.state.db,
            arduino=app.state.arduino,              
        )
    }
    
    yield
    # ---- shutdown ----
    for cam in app.state.cameras.values():
        cam.stop_monitoring()
    app.state.arduino.close()                       
    app.state.db.close()


app = FastAPI(title="InspectVision API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(base_router)
app.include_router(detect_router)
app.include_router(historyLogs_router)