"""arXiv Atom feed client for defense-relevant preprint ingestion.

Searches by title keywords. Returns raw item dicts ready for database.add_item().
No API key required.
"""
from __future__ import annotations

import xml.etree.ElementTree as ET

import requests

from config import ARXIV_NAMESPACE, ARXIV_AFFILIATION_NS, ARXIV_SEARCHES

_BASE = "https://export.arxiv.org/api/query"
_TIMEOUT = 20
_NS = ARXIV_NAMESPACE
_AFF_NS = ARXIV_AFFILIATION_NS


def _extract_affiliations(entry: ET.Element) -> list[str]:
    """Extract author affiliations from an arXiv Atom entry."""
    affiliations: list[str] = []
    for author in entry.findall(f"{{{_NS}}}author"):
        aff_el = author.find(f"{{{_AFF_NS}}}affiliation")
        if aff_el is not None and aff_el.text:
            aff = aff_el.text.strip()
            if aff and aff not in affiliations:
                affiliations.append(aff)
    return affiliations


def fetch(query: str, max_results: int = 5) -> list[dict]:
    """Fetch papers from arXiv matching query. Returns list of raw item dicts."""
    try:
        resp = requests.get(
            _BASE,
            params={
                "search_query": query,
                "max_results": max_results,
                "sortBy": "submittedDate",
                "sortOrder": "descending",
            },
            timeout=_TIMEOUT,
        )
        resp.raise_for_status()
        root = ET.fromstring(resp.text)
    except Exception:
        return []

    items = []
    for entry in root.findall(f"{{{_NS}}}entry"):
        title_el = entry.find(f"{{{_NS}}}title")
        summary_el = entry.find(f"{{{_NS}}}summary")
        id_el = entry.find(f"{{{_NS}}}id")
        published_el = entry.find(f"{{{_NS}}}published")

        title = (title_el.text or "").strip().replace("\n", " ") if title_el is not None else ""
        abstract = (summary_el.text or "").strip() if summary_el is not None else ""
        url = (id_el.text or "").strip() if id_el is not None else ""
        date = (published_el.text or "")[:10] if published_el is not None else ""

        if not title or not url:
            continue

        # Use the arxiv ID (last segment of URL) as external_id
        external_id = url.rstrip("/").rsplit("/", 1)[-1]

        affiliations = _extract_affiliations(entry)

        items.append({
            "source":          "arxiv",
            "external_id":     external_id,
            "title":           title,
            "abstract":        abstract[:1500],
            "url":             url,
            "published_date":  date,
            "raw_institutions": affiliations,
        })
    return items


def fetch_all() -> list[dict]:
    """Run all configured arXiv searches and deduplicate by external_id."""
    seen: set[str] = set()
    results: list[dict] = []
    for query, max_r in ARXIV_SEARCHES:
        for item in fetch(query, max_results=max_r):
            if item["external_id"] not in seen:
                seen.add(item["external_id"])
                results.append(item)
    return results
