from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse


detect_router = APIRouter(prefix="/api/v1", tags=["detect"])
def _get_camera(request: Request, cam_id: str):
    camera = request.app.state.cameras.get(cam_id)
    if camera is None:
        raise HTTPException(status_code=404, detail="Camera not found")
    return camera

@detect_router.get("/{cam_id}/feed")
def get_camera_feed(request: Request, cam_id: str):
    camera = _get_camera(request, cam_id)
    return StreamingResponse(
        camera.generate_frames(),
        media_type="multipart/x-mixed-replace; boundary=frame",
    )

@detect_router.post("/{cam_id}/start")
def start_camera_monitoring(request: Request, cam_id: str):
    return _get_camera(request, cam_id).start_monitoring()


@detect_router.post("/{cam_id}/stop")
def stop_camera_monitoring(request: Request, cam_id: str):
    return _get_camera(request, cam_id).stop_monitoring()


@detect_router.get("/{cam_id}/stats")
def get_camera_stats(request: Request, cam_id: str):
    return _get_camera(request, cam_id).get_stats()


@detect_router.get("/{cam_id}/live_session_logs")
def get_camera_live_logs(request: Request, cam_id: str):
    return _get_camera(request, cam_id).live_session_logs