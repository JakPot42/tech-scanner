"""Generates the 'Weekly Tech Watch' markdown report.

Aggregates classified items from the database and produces a structured
markdown document stored both in the DB and on disk.
"""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

from config import DUAL_USE_TIERS, REPORTS_DIR, DEFAULT_REPORT_DAYS

_TIER_EMOJI = {
    "CRITICAL": "🔴",
    "HIGH":     "🟡",
    "MEDIUM":   "🔵",
    "LOW":      "⚪",
}

_SOURCE_LABEL = {
    "arxiv":  "arXiv preprint",
    "patent": "USPTO patent",
    "darpa":  "DARPA solicitation",
}


def _trl_label(trl: int | None) -> str:
    if trl is None:
        return "Unknown"
    if trl <= 3:
        return f"TRL {trl} (Basic Research)"
    if trl <= 6:
        return f"TRL {trl} (Applied / Proof-of-Concept)"
    return f"TRL {trl} (Development / Integration)"


def generate(items: list[dict], period_days: int = DEFAULT_REPORT_DAYS) -> str:
    """Build the Weekly Tech Watch markdown from a list of classified items.

    items: list of row dicts from ScannerDB.get_classified_items()
    Returns a markdown string.
    """
    now = datetime.now(timezone.utc)
    date_str = now.strftime("%B %d, %Y")
    period_start = (now - timedelta(days=period_days)).strftime("%B %d")

    lines: list[str] = []
    lines.append(f"# Weekly Tech Watch — {date_str}")
    lines.append(f"*Coverage: {period_start} – {now.strftime('%B %d, %Y')} | "
                 f"{len(items)} items classified*")
    lines.append("")
    lines.append(
        "> **Scope:** Technology trends and institutional activity only. "
        "Individual researchers are not profiled."
    )
    lines.append("")

    if not items:
        lines.append("*No classified items in the selected period.*")
        return "\n".join(lines)

    # ── Section 1: High / Critical Alerts ────────────────────────────────────

    critical_high = [i for i in items if i.get("dual_use_tier") in ("CRITICAL", "HIGH")]
    lines.append("---")
    lines.append("")
    lines.append("## High & Critical Dual-Use Alerts")
    lines.append("")

    if not critical_high:
        lines.append("*No CRITICAL or HIGH items in this period.*")
    else:
        for item in critical_high[:10]:
            tier = item.get("dual_use_tier", "")
            emoji = _TIER_EMOJI.get(tier, "")
            source = _SOURCE_LABEL.get(item.get("source", ""), item.get("source", ""))
            lines.append(
                f"### {emoji} {item['title']}"
            )
            lines.append(
                f"**Source:** {source} &nbsp;|&nbsp; "
                f"**Domain:** {item.get('tech_domain', 'Unknown')} &nbsp;|&nbsp; "
                f"**{_trl_label(item.get('trl'))}** &nbsp;|&nbsp; "
                f"**Novelty:** {item.get('novelty_score', '?')}/10"
            )
            if item.get("trend_label"):
                lines.append(f"*Trend: {item['trend_label']}*")
            if item.get("key_finding"):
                lines.append(f"\n{item['key_finding']}")
            insts = json.loads(item.get("canonical_institutions") or "[]")
            if insts:
                lines.append(f"\n**Institutions:** {', '.join(insts)}")
            if item.get("url"):
                lines.append(f"\n[View source]({item['url']})")
            lines.append("")

    # ── Section 2: Technology Domain Breakdown ───────────────────────────────

    lines.append("---")
    lines.append("")
    lines.append("## Technology Domain Activity")
    lines.append("")

    domain_items: dict[str, list[dict]] = defaultdict(list)
    for item in items:
        d = item.get("tech_domain") or "Unknown"
        domain_items[d].append(item)

    for domain, domain_list in sorted(domain_items.items(), key=lambda x: -len(x[1])):
        tier_counts = Counter(i.get("dual_use_tier") for i in domain_list)
        tier_summary = " / ".join(
            f"{_TIER_EMOJI.get(t, '')} {tier_counts[t]} {t}"
            for t in DUAL_USE_TIERS
            if tier_counts.get(t)
        )
        lines.append(f"### {domain} ({len(domain_list)} items)")
        lines.append(f"*Tiers: {tier_summary}*")
        lines.append("")
        for item in sorted(domain_list, key=lambda x: -(x.get("novelty_score") or 0))[:3]:
            tier_e = _TIER_EMOJI.get(item.get("dual_use_tier", ""), "")
            source_s = _SOURCE_LABEL.get(item.get("source", ""), "")
            lines.append(f"- {tier_e} **{item['title']}** ({source_s})")
            if item.get("trend_label"):
                lines.append(f"  *{item['trend_label']}*")
        lines.append("")

    # ── Section 3: Institutional Activity ────────────────────────────────────

    lines.append("---")
    lines.append("")
    lines.append("## Institutional Activity")
    lines.append("")
    lines.append("*Tracked at institution level. Counts reflect volume of tech activity, not endorsement.*")
    lines.append("")

    inst_domain_map: dict[str, Counter] = defaultdict(Counter)
    for item in items:
        insts = json.loads(item.get("canonical_institutions") or "[]")
        domain = item.get("tech_domain") or "Unknown"
        for inst in insts:
            inst_domain_map[inst][domain] += 1

    if not inst_domain_map:
        lines.append("*No institution data in this period.*")
    else:
        inst_totals = {inst: sum(c.values()) for inst, c in inst_domain_map.items()}
        top_insts = sorted(inst_totals, key=lambda x: -inst_totals[x])[:15]
        lines.append("| Institution | Total Items | Top Domains |")
        lines.append("|---|---|---|")
        for inst in top_insts:
            total = inst_totals[inst]
            top_domains = ", ".join(
                d for d, _ in inst_domain_map[inst].most_common(2)
            )
            lines.append(f"| {inst} | {total} | {top_domains} |")
        lines.append("")

    # ── Section 4: DARPA Solicitations ───────────────────────────────────────

    darpa_items = [i for i in items if i.get("source") == "darpa"]
    if darpa_items:
        lines.append("---")
        lines.append("")
        lines.append("## DARPA Solicitations")
        lines.append("")
        for item in darpa_items:
            tier_e = _TIER_EMOJI.get(item.get("dual_use_tier", ""), "")
            lines.append(f"### {tier_e} {item['title']}")
            lines.append(
                f"**Domain:** {item.get('tech_domain', 'Unknown')} &nbsp;|&nbsp; "
                f"**Dual-Use:** {item.get('dual_use_tier', '?')} &nbsp;|&nbsp; "
                f"**{_trl_label(item.get('trl'))}**"
            )
            if item.get("key_finding"):
                lines.append(f"\n{item['key_finding']}")
            if item.get("url"):
                lines.append(f"\n[View on SAM.gov]({item['url']})")
            lines.append("")

    # ── Footer ────────────────────────────────────────────────────────────────

    source_counts = Counter(i.get("source") for i in items)
    lines.append("---")
    lines.append("")
    lines.append("## Report Metadata")
    lines.append("")
    lines.append(f"- **Generated:** {now.strftime('%Y-%m-%d %H:%M UTC')}")
    lines.append(f"- **Sources:** "
                 f"arXiv ({source_counts.get('arxiv', 0)}) | "
                 f"USPTO ({source_counts.get('patent', 0)}) | "
                 f"DARPA solicitations ({source_counts.get('darpa', 0)})")
    lines.append(f"- **Classification model:** claude-haiku-4-5-20251001")
    lines.append(f"- **Framing:** Technology and institution level only. "
                 "No individual researcher profiling.")
    lines.append("")

    return "\n".join(lines)


def save_to_disk(markdown: str, title: str) -> Path:
    """Write the report to the reports/ directory."""
    out_dir = Path(REPORTS_DIR)
    out_dir.mkdir(exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M")
    safe_title = "".join(c if c.isalnum() or c in " _-" else "" for c in title).strip().replace(" ", "_")
    filename = f"{timestamp}_{safe_title[:40]}.md"
    path = out_dir / filename
    path.write_text(markdown, encoding="utf-8")
    return path
