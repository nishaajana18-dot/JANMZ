from __future__ import annotations

import json
from typing import Any
from urllib.parse import quote
from urllib.request import urlopen
from xml.etree import ElementTree


def fetch_research_resources(topic: str, area: str, limit: int = 6) -> list[dict[str, Any]]:
    query = f"{topic} {area}".strip()
    resources: list[dict[str, Any]] = []
    resources.extend(_fetch_arxiv(query, limit=3))
    resources.extend(_fetch_crossref(query, limit=3))
    return resources[:limit]


def _fetch_arxiv(query: str, limit: int) -> list[dict[str, Any]]:
    url = (
        "https://export.arxiv.org/api/query?search_query=all:"
        f"{quote(query)}&start=0&max_results={limit}&sortBy=relevance&sortOrder=descending"
    )
    try:
        with urlopen(url, timeout=8) as response:
            xml_text = response.read()
        root = ElementTree.fromstring(xml_text)
    except Exception:
        return []

    ns = {"atom": "http://www.w3.org/2005/Atom"}
    items: list[dict[str, Any]] = []
    for entry in root.findall("atom:entry", ns):
        title = (entry.findtext("atom:title", default="", namespaces=ns) or "").strip()
        link = entry.findtext("atom:id", default="", namespaces=ns)
        summary = (entry.findtext("atom:summary", default="", namespaces=ns) or "").strip()
        published = entry.findtext("atom:published", default="", namespaces=ns)
        if title and link:
            items.append(
                {
                    "source": "arXiv",
                    "title": title,
                    "url": link,
                    "summary": summary[:280],
                    "published": published[:10],
                }
            )
    return items


def _fetch_crossref(query: str, limit: int) -> list[dict[str, Any]]:
    url = (
        "https://api.crossref.org/works?rows="
        f"{limit}&query.title={quote(query)}&select=title,URL,issued,container-title"
    )
    try:
        with urlopen(url, timeout=8) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except Exception:
        return []

    items: list[dict[str, Any]] = []
    for item in payload.get("message", {}).get("items", []):
        title_list = item.get("title") or []
        title = title_list[0] if title_list else ""
        if not title:
            continue
        issued = item.get("issued", {}).get("date-parts", [[None]])[0]
        published = "-".join(str(part) for part in issued if part is not None)
        container = item.get("container-title") or []
        journal = container[0] if container else ""
        items.append(
            {
                "source": "Crossref",
                "title": title,
                "url": item.get("URL", ""),
                "summary": journal,
                "published": published,
            }
        )
    return items
