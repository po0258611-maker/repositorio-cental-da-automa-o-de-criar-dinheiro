"""
AME - Real Research Engine
Provides real web research through configured providers. It never returns fabricated
search results: when no provider is configured, the result is explicitly NOT_CONFIGURED.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import hashlib

import httpx

from app.core.config import settings
from app.core.observability import logger


class ResearchError(RuntimeError):
    pass


class ResearchEngine:
    def __init__(self) -> None:
        self.timeout = 20.0

    async def search(self, query: str, limit: int = 5) -> Dict[str, Any]:
        query = (query or "").strip()
        if not query:
            return {"status": "INVALID_QUERY", "query": query, "results": [], "evidence": []}

        provider = (settings.research_provider or "").lower()
        if provider == "tavily" and settings.tavily_api_key:
            return await self._tavily(query, limit)
        if provider == "serper" and settings.serper_api_key:
            return await self._serper(query, limit)

        # Automatic fallback between explicitly configured providers.
        if settings.tavily_api_key:
            return await self._tavily(query, limit)
        if settings.serper_api_key:
            return await self._serper(query, limit)

        return {
            "status": "NOT_CONFIGURED",
            "query": query,
            "provider": provider or None,
            "results": [],
            "evidence": [],
            "message": "Configure TAVILY_API_KEY or SERPER_API_KEY for real web research.",
        }

    async def fetch_url(self, url: str) -> Dict[str, Any]:
        url = (url or "").strip()
        if not url.startswith(("http://", "https://")):
            return {"status": "INVALID_URL", "url": url, "content": None}

        try:
            async with httpx.AsyncClient(
                timeout=self.timeout,
                follow_redirects=True,
                headers={"User-Agent": "AME-ResearchEngine/1.0"},
            ) as client:
                response = await client.get(url)
                response.raise_for_status()
                text = response.text[:100_000]
                evidence = self._evidence(
                    source_url=str(response.url),
                    title=str(response.url),
                    content=text,
                    provider="direct_http",
                )
                return {
                    "status": "OK",
                    "url": str(response.url),
                    "status_code": response.status_code,
                    "content": text,
                    "evidence": evidence,
                }
        except Exception as exc:
            logger.error("research_fetch_failed", url=url, error=str(exc))
            return {"status": "ERROR", "url": url, "content": None, "error": str(exc)}

    async def _tavily(self, query: str, limit: int) -> Dict[str, Any]:
        endpoint = "https://api.tavily.com/search"
        payload = {
            "api_key": settings.tavily_api_key,
            "query": query,
            "search_depth": "advanced",
            "max_results": max(1, min(limit, 20)),
            "include_answer": True,
            "include_raw_content": False,
        }
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(endpoint, json=payload)
                response.raise_for_status()
                data = response.json()
            results = data.get("results", [])
            evidence = [
                self._evidence(
                    source_url=item.get("url", ""),
                    title=item.get("title", ""),
                    content=item.get("content", ""),
                    provider="tavily",
                )
                for item in results
            ]
            return {
                "status": "OK",
                "provider": "tavily",
                "query": query,
                "answer": data.get("answer"),
                "results": results,
                "evidence": evidence,
                "collected_at": datetime.now(timezone.utc).isoformat(),
            }
        except Exception as exc:
            logger.error("tavily_search_failed", query=query, error=str(exc))
            return {"status": "ERROR", "provider": "tavily", "query": query, "results": [], "evidence": [], "error": str(exc)}

    async def _serper(self, query: str, limit: int) -> Dict[str, Any]:
        endpoint = "https://google.serper.dev/search"
        headers = {"X-API-KEY": settings.serper_api_key or "", "Content-Type": "application/json"}
        payload = {"q": query, "num": max(1, min(limit, 20))}
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(endpoint, headers=headers, json=payload)
                response.raise_for_status()
                data = response.json()
            results = data.get("organic", [])
            normalized = [
                {
                    "title": item.get("title"),
                    "url": item.get("link"),
                    "content": item.get("snippet", ""),
                }
                for item in results
            ]
            evidence = [
                self._evidence(
                    source_url=item.get("url", ""),
                    title=item.get("title", ""),
                    content=item.get("content", ""),
                    provider="serper",
                )
                for item in normalized
            ]
            return {
                "status": "OK",
                "provider": "serper",
                "query": query,
                "results": normalized,
                "evidence": evidence,
                "collected_at": datetime.now(timezone.utc).isoformat(),
            }
        except Exception as exc:
            logger.error("serper_search_failed", query=query, error=str(exc))
            return {"status": "ERROR", "provider": "serper", "query": query, "results": [], "evidence": [], "error": str(exc)}

    @staticmethod
    def _evidence(source_url: str, title: str, content: str, provider: str) -> Dict[str, Any]:
        material = f"{source_url}\n{title}\n{content}".encode("utf-8")
        return {
            "id": hashlib.sha256(material).hexdigest()[:24],
            "source_url": source_url,
            "title": title,
            "excerpt": (content or "")[:4000],
            "provider": provider,
            "collected_at": datetime.now(timezone.utc).isoformat(),
            "type": "REAL_WEB_EVIDENCE",
        }


research_engine = ResearchEngine()
