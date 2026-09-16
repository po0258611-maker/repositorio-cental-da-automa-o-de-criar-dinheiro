"""
AME - IMAGE_PROVIDER abstraction
Desacoplado para trocar fornecedores (Replicate, Stability, OpenAI DALL-E, etc)
"""
from typing import Dict, Any, Optional
from app.core.observability import logger
from app.core.config import settings
import os

class ImageProvider:
    def __init__(self):
        self.provider = "mock"
        if os.getenv("REPLICATE_API_KEY"):
            self.provider = "replicate"
        elif os.getenv("STABILITY_API_KEY"):
            self.provider = "stability"
        elif settings.openai_api_key:
            self.provider = "openai"

    def generate(self, prompt: str, width: int = 1024, height: int = 1024, style: str = "realistic", n: int = 1) -> Dict[str, Any]:
        logger.info("image_generate", prompt=prompt[:80], provider=self.provider, width=width, height=height)
        # Mock gera SVG placeholder + metadata
        if self.provider == "openai" and settings.openai_api_key and settings.openai_api_key.startswith("sk-"):
            try:
                from openai import OpenAI
                client = OpenAI(api_key=settings.openai_api_key)
                resp = client.images.generate(model="dall-e-3", prompt=prompt, size=f"{width}x{height}", n=1)
                return {"provider": "openai", "url": resp.data[0].url, "prompt": prompt, "cost": 0.04}
            except Exception as e:
                logger.error("image_openai_failed", error=str(e))
        
        # Fallback mock - retorna SVG data uri
        svg = f"<svg width='{width}' height='{height}' xmlns='http://www.w3.org/2000/svg'><rect width='100%' height='100%' fill='#0a0a0f'/><text x='50%' y='50%' fill='#00d084' font-size='24' text-anchor='middle' font-family='system-ui'>{prompt[:40]}</text></svg>"
        import base64
        b64 = base64.b64encode(svg.encode()).decode()
        data_uri = f"data:image/svg+xml;base64,{b64}"
        return {"provider": "mock", "url": data_uri, "prompt": prompt, "cost": 0.0, "mock": True, "svg": svg}

    def edit(self, image_path: str, prompt: str) -> Dict[str, Any]:
        return {"provider": self.provider, "edited": image_path, "prompt": prompt, "cost": 0.0}

image_provider = ImageProvider()
