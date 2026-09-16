"""
AME - BROWSER / WEB AUTOMATION provider
Navegação, coleta, preenchimento, monitoramento, publicação (quando permitido)
"""
from typing import Dict, Any, Optional, List
from app.core.observability import logger
from pathlib import Path

class BrowserProvider:
    def __init__(self):
        self.headless = True
        self.timeout = 30000

    def navigate(self, url: str) -> Dict[str, Any]:
        logger.info("browser_navigate", url=url)
        # Mock - em prod usaria playwright
        return {"url": url, "status": 200, "title": f"Page {url}", "mock": True}

    def scrape(self, url: str, selector: str = "body", extract: str = "text") -> Dict[str, Any]:
        logger.info("browser_scrape", url=url, selector=selector)
        # Tenta com requests+bs4 se disponível
        try:
            import requests
            from bs4 import BeautifulSoup
            resp = requests.get(url, timeout=10, headers={"User-Agent": "AME/1.0"})
            soup = BeautifulSoup(resp.text, "lxml")
            els = soup.select(selector)
            data = [el.get_text(strip=True)[:300] for el in els[:5]]
            return {"url": url, "data": data, "count": len(data), "mock": False}
        except Exception as e:
            logger.error("browser_scrape_failed", error=str(e))
            return {"url": url, "data": [f"Mock data for {url}"], "error": str(e), "mock": True}

    def fill_form(self, url: str, fields: Dict[str, str]) -> Dict[str, Any]:
        logger.info("browser_fill_form", url=url, fields=list(fields.keys()))
        return {"url": url, "fields": fields, "submitted": True, "mock": True}

    def screenshot(self, url: str, path: str = "exports/screenshots/shot.png") -> Dict[str, Any]:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        Path(path).write_text(f"Screenshot mock for {url}", encoding="utf-8")
        return {"url": url, "path": path, "mock": True}

    def monitor_price(self, url: str, selector: str = ".price") -> Dict[str, Any]:
        result = self.scrape(url, selector)
        # Simula preço
        import random
        price = round(random.uniform(47, 297), 2)
        return {"url": url, "price": price, "selector": selector, "raw": result}

browser_provider = BrowserProvider()
