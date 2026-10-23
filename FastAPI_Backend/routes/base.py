from fastapi import APIRouter


base_router = APIRouter(tags=["base"])
@base_router.get("/")
def root():
    return {"status": "Online", "system": "InspectVision Core System"}