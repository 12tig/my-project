# app/config.py
import os

# 配置Git仓库信息
class Config:
    listen_host = "127.0.0.1"
    listen_port = 8000
    reload_debug = True
    proxy = {
        "http": os.getenv("HTTP_PROXY", ""),
        "https": os.getenv("HTTPS_PROXY", ""),
    }
    project_version = "1.0.0"
    ui_language = "en"
    
config = Config()
