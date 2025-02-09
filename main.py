import os
import uvicorn
from loguru import logger
from app.config import config
from git_changelog.cli import build_and_render

def generate_changelog():
    """生成 CHANGELOG.md 文件"""
    try:
        os.makedirs("changelog", exist_ok=True)  # 确保 changelog 目录存在
        build_and_render(
            repository=".",
            output="changelog/CHANGELOG.md",
            convention="angular",
            provider="github",
            template="keepachangelog",
            parse_trailers=True,
            parse_refs=False,
            sections=["build", "deps", "feat", "fix", "refactor"],
            versioning="pep440",
            bump="1.1.2",
            in_place=False,
        )
        logger.info("✅ CHANGELOG.md 生成成功！")
    except Exception as e:
        logger.error(f"❌ 生成 CHANGELOG.md 失败: {str(e)}")

def start_server():
    """启动 FastAPI 服务器"""
    logger.info(f"🚀 FastAPI 服务器启动: http://{config.listen_host}:{config.listen_port}")
    uvicorn.run(
        app="app.asgi:app",  # 确保 `app/asgi.py` 存在
        host=config.listen_host,
        port=config.listen_port,
        reload=config.reload_debug,
        log_level="debug",  # 让日志更详细
    )

if __name__ == "__main__":
    generate_changelog()
    start_server()
