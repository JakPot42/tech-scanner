"""DARPA solicitation client via SAM.gov Opportunities API v2.

Requires SAM_API_KEY environment variable. If not set, returns empty list
and the caller skips this source gracefully.

Searches for DARPA Broad Agency Announcements (BAAs) and Special Notices.
"""
from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone

import requests

from config import DARPA_DEPT_CODE, DARPA_SUBTIER_NAME, SAM_BASE_URL

_TIMEOUT = 20


def fetch(days_back: int = 90, limit: int = 10) -> list[dict]:
    """Fetch recent DARPA solicitations from SAM.gov.

    Returns raw item dicts. Returns empty list (no exception) if:
    - SAM_API_KEY not set
    - API call fails
    """
    api_key = os.environ.get("SAM_API_KEY", "")
    if not api_key:
        return []

    now = datetime.now(timezone.utc)
    posted_from = (now - timedelta(days=days_back)).strftime("%m/%d/%Y")
    posted_to = now.strftime("%m/%d/%Y")

    try:
        resp = requests.get(
            SAM_BASE_URL,
            params={
                "api_key": api_key,
                "limit": limit,
                "postedFrom": posted_from,
                "postedTo": posted_to,
                "organizationCode": DARPA_DEPT_CODE,
                "typeOfSetAsideDescription": "",
                "ptype": "o,k",
            },
            timeout=_TIMEOUT,
        )
        resp.raise_for_status()
        data = resp.json()
    except Exception:
        return []

    items = []
    for opp in data.get("opportunitiesData") or []:
        # Filter to DARPA-issued solicitations by subtier name
        dept = (opp.get("subtierAgencyName") or "").upper()
        if DARPA_SUBTIER_NAME not in dept and "DARPA" not in dept:
            continue

        sol_id = (opp.get("solicitationNumber") or opp.get("noticeId") or "").strip()
        title = (opp.get("title") or "").strip()
        if not title:
            continue

        external_id = sol_id or title[:40]
        description = (opp.get("description") or "")[:1500]
        posted_date = (opp.get("postedDate") or "")[:10]
        url = opp.get("uiLink") or ""

        items.append({
            "source":           "darpa",
            "external_id":      external_id,
            "title":            title,
            "abstract":         description,
            "url":              url,
            "published_date":   posted_date,
            "raw_institutions": ["DARPA"],
        })
    return items
