from concurrent.futures import ThreadPoolExecutor
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from ultralytics import YOLO

from controllers.camera import CameraStreamManager
from helpers import config
from helpers.mysql_db import DatabaseHandler
from routes.base import base_router
from routes.data import data_router
from routes.detect import detect_router


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
    app.state.model = YOLO(config.MODEL_PATH)
    app.state.executor = ThreadPoolExecutor(max_workers=config.MAX_WORKERS)
    app.state.cameras = {
        "1": CameraStreamManager(
            camera_id="1",
            model=app.state.model,
            db=app.state.db,
            executor=app.state.executor,
        )
    }
    print("Model Classes:", app.state.model.names)

    yield

    # ---- shutdown ----
    app.state.executor.shutdown(wait=False)
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
app.include_router(data_router)