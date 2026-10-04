# InspectVision 👁️📦

**InspectVision** is an AI-powered real-time visual inspection and quality control system designed for industrial tissue and packaging production lines. Powered by **YOLO**, **OpenCV**, and **FastAPI**, the system automates package counting, detects damaged/defective products, highlights anomalies dynamically in the video stream, and logs inspection data for auditability.

---

## ✨ Features

- **Real-time Object Detection & Tracking:** Leverages YOLO and object tracking to follow packages as they move along the conveyor belt.
- **Dynamic Anomaly Highlighting:**
  - 🟢 **Normal Packages:** Bounding box and label styled in **Green**.
  - 🔴 **Damaged Packages:** Bounding box and label styled in **Red** (`[DAMAGED]`).
- **Conveyor Line Package Counting:** Uses a horizontal reference line (`CY_LINE = 360`) with an offset threshold (`OFFSET = 35`) and ROI filtering (X-range: 200–800) to ensure accurate package counting without duplicates.
- **Asynchronous Defect Logging:** Extracts crop images of damaged items and logs defect details (Track ID, Timestamp, Status) to a MySQL database asynchronously via executor threads.
- **Modern Dashboard UI:** Includes dynamic KPI display (Total Tracked vs. Defective Packages) and live inspection history tables using React (TypeScript).

---

## 🛠️ Tech Stack

### **Backend**
- **Language:** Python 3.10+
- **Framework:** FastAPI, Uvicorn
- **Computer Vision & AI:** OpenCV, Ultralytics YOLO
- **Database:** MySQL
- **Concurrency:** `concurrent.futures.ThreadPoolExecutor`

### **Frontend**
- **Framework:** React with TypeScript
- **Styling:** Tailwind CSS / Custom Components

---

## 🏗️ System Logic & Configuration

```
┌─────────────────────────────────────────────────────────────┐
│                   InspectVision Pipeline                    │
│                                                             │
│   Video Stream  ──>  ROI Filter (200 <= cx <= 800)          │
│                              │                              │
│                              ▼                              │
│                      YOLO Tracking                          │
│                              │                              │
│               ┌──────────────┴──────────────┐               │
│               ▼                             ▼               │
│      Class 0: Damaged             Class 1: Normal           │
│    (Red Box & Label)            (Green Box & Label)         │
│               │                             │               │
│               └──────────────┬──────────────┘               │
│                              │                              │
│                              ▼                              │
│              Crosses CY_LINE (360 ± 35 px)?                 │
│                              │                              │
│                    ┌─────────┴─────────┐                    │
│                   YES                 NO                    │
│                    │                   │                    │
│                    ▼                   ▼                    │
│          Increment Total Count    Continue Track           │
│                    │                                        │
│          Is Package Damaged?                                │
│           ├── YES ──> Save Crop & Log to MySQL              │
│           └── NO  ──> Skip DB Logging                       │
└─────────────────────────────────────────────────────────────┘
```

### Model Classification Map
| Class ID | Status | Action / Bounding Box |
| :--- | :--- | :--- |
| **`0`** | **Damaged** | Red Bounding Box `(0, 0, 255)`, Save Crop & Log Defect |
| **`1`** | **Normal** | Green Bounding Box `(0, 255, 0)`, Count Only |

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- Node.js & npm (for Frontend)
- MySQL Database

---

### 1️⃣ Backend Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/hossam-ibrahim27/FineDemo.git
   cd FineDemo/FastAPI_Backend
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Configuration (`.env`):**
   Create a `.env` file in the backend root directory:
   ```env
   DB_HOST=localhost
   DB_USER=root
   DB_PASSWORD=your_password
   DB_NAME=inspectvision_db
   ```

5. **Run the FastAPI Server:**
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```
   *The API will be accessible at `http://localhost:8000` (Docs at `/docs`).*

---

### 2️⃣ Frontend Setup

1. **Navigate to the frontend folder:**
   ```bash
   cd ../frontend
   ```

2. **Install dependencies & start development server:**
   ```bash
   npm install
   npm run dev
   ```
   *Access the web panel at `http://localhost:5173`.*

---

## 🌐 Deployment Notes
- **Frontend Application:** [https://car-prediction-reactjs.vercel.app](https://fine-demo-five.vercel.app/) .

---

## 📄 License

This project is created for the **Fine Graduation Project Team (2026)**.
