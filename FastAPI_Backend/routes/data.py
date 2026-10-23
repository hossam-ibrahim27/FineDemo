from fastapi import APIRouter, HTTPException, Request


historyLogs_router = APIRouter(prefix="/api", tags=["data"])
@historyLogs_router.get("/history_logs")
def get_history_logs(request: Request):
    try:
        logs = request.app.state.db.get_all_logs()
        return [
            {
                "Camera": "CAM #1",
                "Track ID": log.get("track_id"),
                "defective": "defective" if log.get("defective") else "good",
                "Time": str(log.get("created_at", "")),
            }
            for log in logs
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))