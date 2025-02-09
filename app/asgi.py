from fastapi import FastAPI
from app.api.youtube import router as youtube_router

app = FastAPI(title="Video Pipeline API", version="1.0")

# 注册 API 路由
app.include_router(youtube_router, prefix="/api/v2/youtube")

@app.get("/")
async def root():
    return {"message": "Welcome to the Video Pipeline API!"}
