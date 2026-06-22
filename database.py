"""SQLite persistence for the Emerging Tech Horizon Scanner.

Two tables:
  items   — ingested papers/patents/solicitations + Claude assessments
  reports — generated Weekly Tech Watch markdown reports
"""
from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path


_CREATE_ITEMS = """
CREATE TABLE IF NOT EXISTS items (
    id                    INTEGER PRIMARY KEY AUTOINCREMENT,
    source                TEXT    NOT NULL,
    external_id           TEXT    NOT NULL,
    title                 TEXT    NOT NULL,
    abstract              TEXT,
    url                   TEXT,
    published_date        TEXT,
    raw_institutions      TEXT,
    ingested_at           TEXT    NOT NULL,
    status                TEXT    NOT NULL DEFAULT 'pending',
    tech_domain           TEXT,
    novelty_score         INTEGER,
    dual_use_tier         TEXT,
    trl                   INTEGER,
    trend_label           TEXT,
    key_finding           TEXT,
    canonical_institutions TEXT,
    classified_at         TEXT,
    UNIQUE(source, external_id)
);
"""

_CREATE_REPORTS = """
CREATE TABLE IF NOT EXISTS reports (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    title         TEXT    NOT NULL,
    period_start  TEXT,
    period_end    TEXT,
    item_count    INTEGER,
    markdown_body TEXT    NOT NULL,
    generated_at  TEXT    NOT NULL
);
"""


class ScannerDB:
    def __init__(self, db_path: str = ":memory:") -> None:
        if db_path != ":memory:":
            Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.executescript(_CREATE_ITEMS + _CREATE_REPORTS)
        self._conn.commit()

    # ── ingestion ─────────────────────────────────────────────────────────────

    def add_item(self, item: dict) -> int | None:
        """Insert a raw item. Returns row id or None if (source, external_id) already exists."""
        if self.external_id_exists(item["source"], item["external_id"]):
            return None
        now = datetime.now(timezone.utc).isoformat()
        cur = self._conn.execute(
            """INSERT INTO items
               (source, external_id, title, abstract, url, published_date,
                raw_institutions, ingested_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                item["source"], item["external_id"], item["title"],
                item.get("abstract", ""), item.get("url", ""),
                item.get("published_date", ""),
                json.dumps(item.get("raw_institutions") or []),
                now,
            ),
        )
        self._conn.commit()
        return cur.lastrowid

    def external_id_exists(self, source: str, external_id: str) -> bool:
        row = self._conn.execute(
            "SELECT 1 FROM items WHERE source=? AND external_id=?",
            (source, external_id),
        ).fetchone()
        return row is not None

    # ── classification ────────────────────────────────────────────────────────

    def mark_classified(self, item_id: int, assessment: dict, canonical_insts: list[str]) -> None:
        now = datetime.now(timezone.utc).isoformat()
        self._conn.execute(
            """UPDATE items SET
               status                = 'done',
               tech_domain           = ?,
               novelty_score         = ?,
               dual_use_tier         = ?,
               trl                   = ?,
               trend_label           = ?,
               key_finding           = ?,
               canonical_institutions = ?,
               classified_at         = ?
               WHERE id = ?""",
            (
                assessment.get("tech_domain"),
                assessment.get("novelty_score"),
                assessment.get("dual_use_tier"),
                assessment.get("trl"),
                assessment.get("trend_label"),
                assessment.get("key_finding"),
                json.dumps(canonical_insts),
                now, item_id,
            ),
        )
        self._conn.commit()

    def mark_error(self, item_id: int) -> None:
        self._conn.execute("UPDATE items SET status='error' WHERE id=?", (item_id,))
        self._conn.commit()

    # ── queries ───────────────────────────────────────────────────────────────

    def get_pending_items(self, limit: int | None = None) -> list[dict]:
        q = "SELECT * FROM items WHERE status='pending' ORDER BY ingested_at ASC"
        if limit:
            q += f" LIMIT {int(limit)}"
        return [dict(r) for r in self._conn.execute(q).fetchall()]

    def get_classified_items(
        self,
        domain: str | None = None,
        tier: str | None = None,
        days: int | None = None,
        limit: int = 100,
    ) -> list[dict]:
        clauses = ["status='done'"]
        params: list = []
        if domain:
            clauses.append("tech_domain=?")
            params.append(domain)
        if tier:
            clauses.append("dual_use_tier=?")
            params.append(tier)
        if days:
            clauses.append("classified_at >= datetime('now', ?)")
            params.append(f"-{days} days")
        where = " AND ".join(clauses)
        rows = self._conn.execute(
            f"SELECT * FROM items WHERE {where} ORDER BY dual_use_tier, novelty_score DESC LIMIT {int(limit)}",
            params,
        ).fetchall()
        return [dict(r) for r in rows]

    def get_stats(self) -> dict:
        status_rows = self._conn.execute(
            "SELECT status, COUNT(*) n FROM items GROUP BY status"
        ).fetchall()
        stats = {r["status"]: r["n"] for r in status_rows}
        tier_rows = self._conn.execute(
            "SELECT dual_use_tier, COUNT(*) n FROM items WHERE status='done' GROUP BY dual_use_tier"
        ).fetchall()
        stats["tiers"] = {r["dual_use_tier"]: r["n"] for r in tier_rows}
        domain_rows = self._conn.execute(
            "SELECT tech_domain, COUNT(*) n FROM items WHERE status='done' GROUP BY tech_domain ORDER BY n DESC"
        ).fetchall()
        stats["domains"] = {r["tech_domain"]: r["n"] for r in domain_rows}
        return stats

    # ── reports ───────────────────────────────────────────────────────────────

    def save_report(self, title: str, markdown_body: str,
                    period_start: str, period_end: str, item_count: int) -> int:
        now = datetime.now(timezone.utc).isoformat()
        cur = self._conn.execute(
            """INSERT INTO reports (title, period_start, period_end, item_count, markdown_body, generated_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (title, period_start, period_end, item_count, markdown_body, now),
        )
        self._conn.commit()
        return cur.lastrowid

    def get_reports(self, limit: int = 20) -> list[dict]:
        rows = self._conn.execute(
            "SELECT id, title, period_start, period_end, item_count, generated_at FROM reports ORDER BY generated_at DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [dict(r) for r in rows]

    def get_report_body(self, report_id: int) -> str | None:
        row = self._conn.execute(
            "SELECT markdown_body FROM reports WHERE id=?", (report_id,)
        ).fetchone()
        return row["markdown_body"] if row else None

    # ── demo seeding ──────────────────────────────────────────────────────────

    def seed_demo(self, seeds: list[dict]) -> int:
        """Insert pre-baked demo items with assessments already populated."""
        now = datetime.now(timezone.utc).isoformat()
        added = 0
        for s in seeds:
            if self.external_id_exists(s["source"], s["external_id"]):
                continue
            self._conn.execute(
                """INSERT INTO items
                   (source, external_id, title, abstract, url, published_date,
                    raw_institutions, ingested_at, status,
                    tech_domain, novelty_score, dual_use_tier, trl,
                    trend_label, key_finding, canonical_institutions, classified_at)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    s["source"], s["external_id"], s["title"],
                    s.get("abstract", ""), s.get("url", ""),
                    s.get("published_date", "2026-06-22"),
                    json.dumps(s.get("raw_institutions") or []),
                    now, "done",
                    s.get("tech_domain"), s.get("novelty_score"),
                    s.get("dual_use_tier"), s.get("trl"),
                    s.get("trend_label"), s.get("key_finding"),
                    json.dumps(s.get("canonical_institutions") or []),
                    now,
                ),
            )
            added += 1
        self._conn.commit()
        return added

    def close(self) -> None:
        self._conn.close()
