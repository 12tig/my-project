from fastapi import APIRouter

router = APIRouter()

@router.get("/download")
async def download_video(url: str):
    return {"status": "success", "message": f"Downloading {url}"}
