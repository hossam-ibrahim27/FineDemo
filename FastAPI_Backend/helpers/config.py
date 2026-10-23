import os
from pathlib import Path
from dotenv import load_dotenv
import torch

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
FRAME_SIZE = (1020, 500)

# Arduino
ARDUINO_PORT = os.getenv("ARDUINO_PORT", "")          # COM7 if windows os
ARDUINO_BAUDRATE = int(os.getenv("ARDUINO_BAUDRATE", 9600))

# Inspection logic (same values as the working script)
CONFIDENCE = float(os.getenv("CONFIDENCE", 0.5))
# NO OF FRAMES BEFORE DETECTING AND MAKE DECISION
VOTES_REQUIRED = int(os.getenv("VOTES_REQUIRED", 5))
# Only boxes bigger than this share of the frame can vote (far packages are unreliable)
MIN_BOX_AREA_RATIO = float(os.getenv("MIN_BOX_AREA_RATIO", 0.02))
# A package not seen for this many frames is considered gone
LOST_FRAMES = int(os.getenv("LOST_FRAMES", 30))
# A package that left with fewer votes than this is ignored
MIN_VOTES_ON_EXIT = int(os.getenv("MIN_VOTES_ON_EXIT", 2))
GOOD_LABEL = "good"
DEFECT_LABEL = "defective"
DEVICE = os.getenv("DEVICE") or ("0" if torch.cuda.is_available() else "cpu")