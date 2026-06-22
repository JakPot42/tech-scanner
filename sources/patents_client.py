"""USPTO PatentsView API client for defense-relevant patent ingestion.

Searches recent patents by keyword. Returns raw item dicts.
No API key required.
"""
from __future__ import annotations

import json

import requests

from config import PATENT_KEYWORDS, PATENT_MAX_PER_QUERY

_BASE = "https://search.patentsview.org/api/v1/patent/"
_TIMEOUT = 20
_FIELDS = [
    "patent_id",
    "patent_title",
    "patent_abstract",
    "patent_date",
    "assignees",
]


def fetch(keyword: str, max_results: int = PATENT_MAX_PER_QUERY) -> list[dict]:
    """Search PatentsView for patents matching keyword. Returns raw item dicts."""
    try:
        params = {
            "q": json.dumps({"_text_any": {"patent_abstract": keyword}}),
            "f": json.dumps(_FIELDS),
            "o": json.dumps({
                "per_page": max_results,
                "sort_by": "patent_date",
                "sort_order": "desc",
            }),
        }
        resp = requests.get(_BASE, params=params, timeout=_TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
    except Exception:
        return []

    items = []
    for p in data.get("patents") or []:
        title = (p.get("patent_title") or "").strip()
        patent_id = (p.get("patent_id") or "").strip()
        if not title or not patent_id:
            continue

        abstract = (p.get("patent_abstract") or "").strip()
        date = (p.get("patent_date") or "")[:10]

        assignees = p.get("assignees") or []
        raw_institutions = [
            a["assignee_organization"]
            for a in assignees
            if a.get("assignee_organization")
        ]

        items.append({
            "source":           "patent",
            "external_id":      patent_id,
            "title":            title,
            "abstract":         abstract[:1500],
            "url":              f"https://patents.google.com/patent/US{patent_id}",
            "published_date":   date,
            "raw_institutions": raw_institutions,
        })
    return items


def fetch_all() -> list[dict]:
    """Run all configured keyword searches and deduplicate by patent_id."""
    seen: set[str] = set()
    results: list[dict] = []
    for keyword in PATENT_KEYWORDS:
        for item in fetch(keyword):
            if item["external_id"] not in seen:
                seen.add(item["external_id"])
                results.append(item)
    return results
