"""
AME - DOCUMENT_PROVIDER
Gera ebooks, PDFs, documentos, templates
"""
from typing import Dict, Any, List, Optional
from pathlib import Path
from app.core.llm_router import llm_router
from app.core.observability import logger
import json

class DocumentProvider:
    def create_ebook(self, title: str, chapters: List[str], author: str = "AME", style: str = "profissional") -> Dict[str, Any]:
        logger.info("document_ebook_create", title=title, chapters=len(chapters))
        ebook = {"title": title, "author": author, "style": style, "chapters": [], "cover": None}
        for ch in chapters:
            prompt = f"Escreva capítulo '{ch}' para ebook '{title}' - 300 palavras, tom {style}, prático, com exemplos"
            content = llm_router.generate(prompt, task_type="medium", max_tokens=500)
            ebook["chapters"].append({"title": ch, "content": content[:1200]})
        # Cover via image_provider
        try:
            from app.providers.image_provider import image_provider
            cover = image_provider.generate(f"Capa ebook '{title}' estilo premium", width=600, height=800)
            ebook["cover"] = cover
        except:
            ebook["cover"] = {"mock": True}
        ebook["total_words"] = sum(len(c["content"].split()) for c in ebook["chapters"])
        ebook["pages"] = len(chapters) * 3
        return ebook

    def create_pdf(self, title: str, content: str, output_path: str = "exports/docs/output.pdf") -> Dict[str, Any]:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        # Simula PDF como HTML que pode ser convertido
        html = f"<html><head><meta charset='utf-8'><title>{title}</title></head><body><h1>{title}</h1><div>{content}</div></body></html>"
        Path(output_path.replace(".pdf", ".html")).write_text(html, encoding="utf-8")
        logger.info("document_pdf_created", title=title, path=output_path)
        return {"path": output_path, "html_path": output_path.replace(".pdf", ".html"), "title": title, "cost": 0.0}

    def create_template(self, name: str, type: str = "notion", content: str = "") -> Dict[str, Any]:
        path = f"exports/templates/{name.replace(' ', '_')}.{type}"
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        Path(path).write_text(content or f"Template {name} - {type}", encoding="utf-8")
        return {"path": path, "name": name, "type": type}

document_provider = DocumentProvider()
