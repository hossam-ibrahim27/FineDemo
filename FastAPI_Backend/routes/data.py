from fastapi import APIRouter, HTTPException, Request

data_router = APIRouter(prefix="/api", tags=["data"])


@data_router.get("/history_logs")
def get_history_logs(request: Request):
    try:
        logs = request.app.state.db.get_all_logs()
        return [
            {
                "Camera": "CAM #1",
                "Track ID": log.get("track_id"),
                "damage": "Damaged" if log.get("damage") else "Normal",
                "Time": str(log.get("created_at", "")),
            }
            for log in logs
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))