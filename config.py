"""All tunable constants for the Emerging Tech Horizon Scanner."""
from __future__ import annotations

# ── Technology taxonomy ─────────────────────────────────────────────────────

TECH_DOMAINS = [
    "Hypersonics & Advanced Propulsion",
    "Directed Energy Weapons",
    "Quantum Computing & Sensing",
    "AI/ML for Defense Applications",
    "Autonomous Systems & Robotics",
    "Biotechnology & Synthetic Biology",
    "Space Systems & SSA",
    "Cyber & Electronic Warfare",
    "Advanced Materials & Manufacturing",
    "Nuclear & Radiological Technologies",
    "Microelectronics & Semiconductors",
    "Communications & 5G/6G",
    "Energy Storage & Power",
    "Sensors & ISR",
]

# Dual-use tier ordering (highest first for display)
DUAL_USE_TIERS = ["CRITICAL", "HIGH", "MEDIUM", "LOW"]

TIER_COLORS = {
    "CRITICAL": "bold red",
    "HIGH":     "bold yellow",
    "MEDIUM":   "cyan",
    "LOW":      "dim",
}

# ── Entity resolution thresholds (adapted from GhostTrace) ──────────────────

FUZZY_AUTO_MERGE_THRESHOLD = 90.0
FUZZY_ADJUDICATE_THRESHOLD = 75.0

# Terms to strip when normalizing institution names
NORMALIZE_SUFFIXES = [
    "inc", "llc", "ltd", "corp", "corporation", "co", "plc", "lp",
    "university", "univ",
    "institute", "inst",
    "laboratory", "lab", "labs", "national laboratory",
    "technologies", "tech",
    "systems", "group", "division", "dept", "department",
    "research", "center", "centre",
]

# ── arXiv searches ──────────────────────────────────────────────────────────

# Each tuple: (query, max_results)
ARXIV_SEARCHES = [
    ("ti:hypersonic",                    5),
    ("ti:directed+energy",               5),
    ("ti:quantum+sensing",               5),
    ("ti:electronic+warfare",            5),
    ("ti:autonomous+unmanned+systems",   5),
    ("ti:neuromorphic",                  5),
]

ARXIV_NAMESPACE = "http://www.w3.org/2005/Atom"
ARXIV_AFFILIATION_NS = "http://arxiv.org/schemas/atom"

# ── USPTO PatentsView searches ──────────────────────────────────────────────

PATENT_KEYWORDS = [
    "hypersonic vehicle propulsion",
    "directed energy weapon",
    "quantum sensor magnetometer",
    "electronic warfare jamming",
    "autonomous swarm UAV",
    "neuromorphic processing",
]
PATENT_MAX_PER_QUERY = 3

# ── DARPA / SAM.gov ─────────────────────────────────────────────────────────

SAM_BASE_URL = "https://api.sam.gov/opportunities/v2/search"
DARPA_DEPT_CODE = "9700"          # DoD department code
DARPA_SUBTIER_NAME = "DEFENSE ADVANCED RESEARCH PROJECTS AGENCY"

# ── Persistence ─────────────────────────────────────────────────────────────

DB_PATH = "tech_scanner.db"
REPORTS_DIR = "reports"

# ── Claude ──────────────────────────────────────────────────────────────────

CLAUDE_MODEL = "claude-haiku-4-5-20251001"
MAX_ABSTRACT_CHARS = 1000   # truncate before sending to Claude

# ── CLI defaults ────────────────────────────────────────────────────────────

DEFAULT_REPORT_DAYS = 7
DEFAULT_BROWSE_LIMIT = 30

FRAMING_NOTE = (
    "Scores at TECHNOLOGY TREND and INSTITUTION level only. "
    "Individual researchers are never flagged or profiled."
)
