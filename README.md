# Emerging Tech Horizon Scanner

CLI tool that monitors arXiv preprints, USPTO patents, and DARPA solicitations for emerging defense-relevant technology trends. Claude Haiku classifies each item by technology domain, dual-use potential, TRL, and novelty. Generates a Weekly Tech Watch markdown report stored in SQLite with browsable history.

**Framing:** Scores at **technology trend and institution level only**. Individual researchers are never flagged or profiled.

## Features

- **Three sources:** arXiv (free), USPTO PatentsView (free), DARPA via SAM.gov (optional key)
- **Claude classification:** tech domain, novelty score, dual-use tier (LOW/MEDIUM/HIGH/CRITICAL), TRL 1-9
- **Institution tracking:** entity_resolver.py adapted from GhostTrace deduplicates institution names ("MIT CSAIL" + "MIT Lincoln Lab" → canonical "Massachusetts Institute of Technology")
- **Weekly Tech Watch:** structured markdown report with CRITICAL/HIGH alerts, domain breakdown, institution activity table, DARPA solicitations section
- **SQLite history:** all items and reports stored; browse with `browse` command

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env
# Add ANTHROPIC_API_KEY to .env
```

## Commands

```bash
# Self-contained demo — no API keys needed
python main.py demo

# Pull live arXiv + USPTO data (no key needed)
# Add SAM_API_KEY to .env for DARPA solicitations
python main.py ingest

# Classify pending items (needs ANTHROPIC_API_KEY)
python main.py classify

# Generate Weekly Tech Watch report
python main.py report

# Browse past reports
python main.py browse

# Browse classified items with filters
python main.py browse --items --tier CRITICAL --domain "Quantum Computing & Sensing"

# Print a specific report body
python main.py browse --report-id 1
```

## Tech Stack

- Python 3.14 | Click | Rich | SQLite (raw) | Requests
- Claude Haiku (`claude-haiku-4-5-20251001`) for classification
- No external vector DB, no ML frameworks
- 127 tests (pytest), all mocked — no real API calls in test suite

## Technology Taxonomy

14 domains: Hypersonics & Advanced Propulsion, Directed Energy Weapons, Quantum Computing & Sensing, AI/ML for Defense Applications, Autonomous Systems & Robotics, Biotechnology & Synthetic Biology, Space Systems & SSA, Cyber & Electronic Warfare, Advanced Materials & Manufacturing, Nuclear & Radiological Technologies, Microelectronics & Semiconductors, Communications & 5G/6G, Energy Storage & Power, Sensors & ISR.

## Architecture

```
main.py              Click CLI (ingest / classify / report / browse / demo)
config.py            Constants, taxonomy, thresholds
database.py          ScannerDB: SQLite items + reports tables
entity_resolver.py   Institution deduplication (adapted from GhostTrace)
sources/
  arxiv_client.py    arXiv Atom feed — no key required
  patents_client.py  USPTO PatentsView API — no key required
  darpa_client.py    SAM.gov Opportunities API — SAM_API_KEY optional
claude_analyst.py    Claude Haiku classification per item
report_generator.py  Weekly Tech Watch markdown generator
seed_data.py         14 pre-classified demo items (no API key needed)
```

## Running Tests

```bash
python -m pytest tests/ -v
# 127 passed
```
