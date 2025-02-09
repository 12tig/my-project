# main.py
import os
import uvicorn
from loguru import logger
from app.config import config
from app.pipeline import VideoPipeline
from git_changelog.cli import build_and_render

def generate_changelog():
    """生成并渲染CHANGELOG.md文件"""
    try:
        build_and_render(
            repository=".",
            output="changelog/CHANGELOG.md",  # 将 changelog 输出到 changelog 文件夹
            convention="angular",
            provider="github",
            template="keepachangelog",
            parse_trailers=True,
            parse_refs=False,
            sections=["build", "deps", "feat", "fix", "refactor"],
            versioning="pep440",
            bump="1.1.2",  # 指定版本号
            in_place=False,
        )
        logger.info("CHANGELOG.md 文件已生成")
    except Exception as e:
        logger.error(f"生成 CHANGELOG.md 文件失败: {str(e)}")

def start_server():
    """启动FastAPI服务器"""
    logger.info(f"Starting server at {config.listen_host}:{config.listen_port}")
    uvicorn.run(
        app="app.asgi:app",
        host=config.listen_host,
        port=config.listen_port,
        reload=config.reload_debug,
        log_level="info",
    )

if __name__ == "__main__":
    # 生成CHANGELOG.md文件
    generate_changelog()

    # 启动服务器
    start_server()
