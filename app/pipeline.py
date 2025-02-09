import requests
import json
import os
import time
from typing import Dict, Any


class VideoPipeline:
    def __init__(self, base_url: str = "http://127.0.0.1:8080"):
        self.base_url = base_url
        self.current_path = os.path.dirname(os.path.abspath(__file__))
        self.resource_path = os.path.join(self.current_path, "resource")
        self.storage_path = os.path.join(self.current_path, "storage")

    def _get_video_path(self, video_name: str) -> str:
        """获取视频路径"""
        return os.path.join(self.resource_path, "videos", f"{video_name}.mp4")

    def _get_script_path(self, script_name: str) -> str:
        """获取脚本路径"""
        return os.path.join(self.resource_path, "scripts", script_name)

    def download_video(self, url: str, resolution: str = "1080p", output_format: str = "mp4", rename: str = None) -> Dict[str, Any]:
        """下载视频"""
        endpoint = f"{self.base_url}/api/v2/youtube/download"
        payload = {
            "url": url,
            "resolution": resolution,
            "output_format": output_format,
            "rename": rename or time.strftime("%Y-%m-%d")
        }

        response = self._send_request(endpoint, payload)
        return response.json()

    def generate_script(self, video_path: str, skip_seconds: int = 0, threshold: int = 30, vision_batch_size: int = 10, vision_llm_provider: str = "gemini") -> Dict[str, Any]:
        """生成脚本"""
        endpoint = f"{self.base_url}/api/v2/scripts/generate"
        payload = {
            "video_path": video_path,
            "skip_seconds": skip_seconds,
            "threshold": threshold,
            "vision_batch_size": vision_batch_size,
            "vision_llm_provider": vision_llm_provider
        }
        response = self._send_request(endpoint, payload)
        return response.json()

    def crop_video(self, video_path: str, script: list) -> Dict[str, Any]:
        """剪辑视频"""
        endpoint = f"{self.base_url}/api/v2/scripts/crop"
        payload = {
            "video_origin_path": video_path,
            "video_script": script
        }
        response = self._send_request(endpoint, payload)
        return response.json()

    def generate_final_video(self, task_id: str, video_path: str, script_path: str, script: list, subclip_videos: Dict[str, str], voice_name: str) -> Dict[str, Any]:
        """生成最终视频"""
        endpoint = f"{self.base_url}/api/v2/scripts/start-subclip"
        request_data = {
            "video_clip_json": script,
            "video_clip_json_path": script_path,
            "video_origin_path": video_path,
            "video_aspect": "16:9",
            "video_language": "zh-CN",
            "voice_name": voice_name,
            "voice_volume": 1,
            "voice_rate": 1.2,
            "voice_pitch": 1,
            "bgm_name": "random",
            "bgm_type": "random",
            "bgm_file": "",
            "bgm_volume": 0.3,
            "subtitle_enabled": True,
            "subtitle_position": "bottom",
            "font_name": "STHeitiMedium.ttc",
            "text_fore_color": "#FFFFFF",
            "text_background_color": "transparent",
            "font_size": 75,
            "stroke_color": "#000000",
            "stroke_width": 1.5,
            "custom_position": 70,
            "n_threads": 8
        }

        payload = {
            "request": request_data,
            "subclip_videos": subclip_videos
        }
        params = {"task_id": task_id}
        response = self._send_request(endpoint, payload, params)
        return response.json()

    def save_script_to_json(self, script: list, script_path: str) -> str:
        """保存脚本到json文件"""
        try:
            os.makedirs(os.path.dirname(script_path), exist_ok=True)  # 确保目录存在
            with open(script_path, 'w', encoding='utf-8') as f:
                json.dump(script, f, ensure_ascii=False, indent=2)
            print(f"脚本已保存到: {script_path}")
            return script_path
        except Exception as e:
            print(f"保存脚本失败: {str(e)}")
            raise

    def _send_request(self, endpoint: str, payload: Dict[str, Any], params: Dict[str, Any] = None) -> requests.Response:
        """发送请求并处理异常"""
        try:
            response = requests.post(endpoint, json=payload, params=params)
            response.raise_for_status()  # 如果状态码不是200，会抛出异常
            return response
        except requests.exceptions.RequestException as e:
            print(f"请求失败: {e}")
            raise

    def run_pipeline(self, task_id: str, script_name: str, youtube_url: str, video_name: str = "null", skip_seconds: int = 0, threshold: int = 30, vision_batch_size: int = 10, vision_llm_provider: str = "gemini", voice_name: str = "zh-CN-YunjianNeural") -> Dict[str, Any]:
        """运行完整的pipeline"""
        try:
            video_path = self._get_video_path(video_name)

            # 判断视频是否存在，不存在则下载
            if not os.path.exists(video_path):
                print(f"视频不存在，开始下载: {video_name}")
                download_result = self.download_video(url=youtube_url, resolution="1080p", output_format="mp4", rename=video_name)
                video_path = download_result["output_path"]
            else:
                print(f"视频已存在: {video_path}")

            # 判断脚本是否存在，不存在则生成
            script_path = self._get_script_path(script_name)
            if os.path.exists(script_path):
                print(f"加载已有脚本: {script_path}")
                with open(script_path, "r", encoding="utf-8") as f:
                    script = json.load(f)
            else:
                print(f"开始生成脚本: {video_name}")
                script_result = self.generate_script(video_path=video_path, skip_seconds=skip_seconds, threshold=threshold, vision_batch_size=vision_batch_size, vision_llm_provider=vision_llm_provider)
                script = script_result["script"]
                print("脚本生成成功")

            # 保存脚本
            print("保存脚本到json文件...")
            self.save_script_to_json(script=script, script_path=script_path)

            # 剪辑视频
            print("开始剪辑视频...")
            crop_result = self.crop_video(video_path=video_path, script=script)
            subclip_videos = crop_result["subclip_videos"]

            # 生成最终视频
            print("开始生成最终视频...")
            self.generate_final_video(
                task_id=task_id,
                video_path=video_path,
                script_path=script_path,
                script=script,
                subclip_videos=subclip_videos,
                voice_name=voice_name
            )

            return {
                "status": "等待异步生成视频",
                "path": os.path.join(self.storage_path, "tasks", task_id)
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}


# 使用示例
if __name__ == "__main__":
    pipeline = VideoPipeline()
    result = pipeline.run_pipeline(
        task_id="test_111901",
        script_name="test.json",
        youtube_url="https://www.youtube.com/watch?v=vLJ7Yed6FQ4",
        video_name="2024-11-19-01",
        skip_seconds=50,
        threshold=35,
        vision_batch_size=10,
        vision_llm_provider="gemini",
        voice_name="zh-CN-YunjianNeural",
    )
    print(result)
