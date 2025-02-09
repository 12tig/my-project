import os
import yt_dlp
from fastapi import APIRouter

router = APIRouter()

# 这里定义下载目录，放在项目根目录
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # 获取当前文件所在目录
ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, "../../"))  # 获取项目根目录
DOWNLOADS_DIR = os.path.join(ROOT_DIR, "downloads")  # 下载目录

# 确保 downloads 目录存在
os.makedirs(DOWNLOADS_DIR, exist_ok=True)

@router.get("/download")
async def download_video(url: str):
    """ 通过 yt-dlp 下载 YouTube 视频 """
    try:
        ydl_opts = {
            "outtmpl": f"{DOWNLOADS_DIR}/%(title)s.%(ext)s",  # 保存路径
            "format": "bestvideo+bestaudio/best",  # 下载最佳质量
            "merge_output_format": "mp4",  # 确保合并为 mp4 格式
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)  # 下载视频
            filename = ydl.prepare_filename(info)  # 获取文件名
            return {"status": "success", "file": filename}
    
    except Exception as e:
        return {"status": "error", "message": str(e)}
