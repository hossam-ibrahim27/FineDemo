import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / "assets" / ".env")

# Database
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "vision_db")
DB_PORT = int(os.getenv("DB_PORT", 3306))

# Model & video
MODEL_PATH = str(BASE_DIR / "models" / "best.pt")
DEFAULT_VIDEO = str(BASE_DIR / "assets" / "videos" / "fineDemo.mp4")

# Detection settings
CY_LINE = 360
OFFSET = 35
ROI_X_MIN = 200
ROI_X_MAX = 800
FRAME_SIZE = (1020, 500)
MAX_WORKERS = 4