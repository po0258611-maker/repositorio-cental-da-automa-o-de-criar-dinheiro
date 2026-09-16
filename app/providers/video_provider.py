"""
AME - VIDEO_PROVIDER abstraction
"""
from typing import Dict, Any
from app.core.observability import logger

class VideoProvider:
    def __init__(self):
        self.provider = "mock"  # pode ser replicate, runway, pika, heygen

    def create_script(self, title: str, script: str, duration: int = 30, voice: str = "pt-BR-female") -> Dict[str, Any]:
        logger.info("video_script_created", title=title, duration=duration)
        return {"provider": self.provider, "title": title, "script": script, "duration": duration, "voice": voice, "cost": 0.0, "mock": True}

    def generate(self, prompt: str, duration: int = 5, style: str = "realistic") -> Dict[str, Any]:
        logger.info("video_generate", prompt=prompt[:80], duration=duration)
        return {"provider": self.provider, "url": "mock://video.mp4", "prompt": prompt, "duration": duration, "cost": 0.5, "mock": True}

    def add_subtitles(self, video_path: str, srt: str) -> Dict[str, Any]:
        return {"video": video_path, "subtitles": "added", "cost": 0.0}

video_provider = VideoProvider()
