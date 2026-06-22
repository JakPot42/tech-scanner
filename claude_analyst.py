"""Claude Haiku classification for emerging technology items.

Classifies at TECHNOLOGY TREND and INSTITUTION level only.
Never profiles individual researchers.
"""
from __future__ import annotations

import json
import re

import anthropic

from config import CLAUDE_MODEL, MAX_ABSTRACT_CHARS, TECH_DOMAINS

_CLIENT: anthropic.Anthropic | None = None


def _client() -> anthropic.Anthropic:
    global _CLIENT
    if _CLIENT is None:
        _CLIENT = anthropic.Anthropic()
    return _CLIENT


_DOMAIN_LIST = "\n".join(f"  - {d}" for d in TECH_DOMAINS)

_SYSTEM = f"""You are a defense technology intelligence analyst. Your role is to classify
emerging technology items for the Emerging Tech Horizon Scanner.

IMPORTANT FRAMING: You score at TECHNOLOGY TREND and INSTITUTION level only.
Never profile, flag, or mention individual researchers by name, nationality, or
ethnicity. Focus exclusively on the technology and the organizations involved.

Respond with a single JSON object — no markdown fences, no preamble.

Required fields:
- tech_domain (string): Choose exactly one from this list:
{_DOMAIN_LIST}
- novelty_score (integer 1-10): How novel/cutting-edge is this relative to the state of art?
  1=incremental improvement, 10=paradigm-shifting breakthrough
- dual_use_tier (string): One of LOW / MEDIUM / HIGH / CRITICAL
  CRITICAL = direct weapons application or WMD-adjacent
  HIGH     = significant military application potential, export-control-adjacent
  MEDIUM   = notable dual-use with civilian primacy
  LOW      = primarily civilian application
- trl (integer 1-9): Technology Readiness Level
  1-3 = basic/fundamental research
  4-6 = applied research / proof-of-concept
  7-9 = system development / operational integration
- trend_label (string): 6-12 word label for the technology trend
- key_finding (string): 1-2 sentences explaining why this matters for defense tech awareness
- institutions (list of strings): Organization names found in the text
  ONLY extract organization names (companies, universities, government labs, agencies)
  Do NOT include individual person names"""


def classify(item: dict) -> dict:
    """Call Claude Haiku to classify a single item.

    Returns assessment dict with keys: tech_domain, novelty_score, dual_use_tier,
    trl, trend_label, key_finding, institutions.

    Raises on API error.
    """
    source_label = {
        "arxiv":  "arXiv preprint",
        "patent": "USPTO patent",
        "darpa":  "DARPA solicitation",
    }.get(item.get("source", ""), "technical document")

    abstract = (item.get("abstract") or "")[:MAX_ABSTRACT_CHARS]
    raw_insts = item.get("raw_institutions") or []
    inst_hint = f"\nKnown affiliations from source metadata: {', '.join(raw_insts)}" if raw_insts else ""

    user_msg = (
        f"Source type: {source_label}\n"
        f"Title: {item['title']}\n"
        f"Abstract/Description: {abstract}"
        f"{inst_hint}"
    )

    msg = _client().messages.create(
        model=CLAUDE_MODEL,
        max_tokens=512,
        system=_SYSTEM,
        messages=[{"role": "user", "content": user_msg}],
    )

    raw = (msg.content[0].text or "").strip()
    # Strip markdown code fences if Claude adds them despite instructions
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)

    parsed = json.loads(raw)

    # Validate/clamp required fields
    parsed["novelty_score"] = max(1, min(10, int(parsed.get("novelty_score") if parsed.get("novelty_score") is not None else 5)))
    trl_raw = parsed.get("trl")
    parsed["trl"] = max(1, min(9, int(trl_raw if trl_raw is not None else 3)))
    if parsed.get("dual_use_tier") not in ("LOW", "MEDIUM", "HIGH", "CRITICAL"):
        parsed["dual_use_tier"] = "MEDIUM"
    if parsed.get("tech_domain") not in TECH_DOMAINS:
        parsed["tech_domain"] = TECH_DOMAINS[0]
    parsed.setdefault("trend_label", "")
    parsed.setdefault("key_finding", "")
    parsed.setdefault("institutions", [])

    return parsed
