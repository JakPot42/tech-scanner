"""Emerging Tech Horizon Scanner — P39.

TECHNOLOGY TREND AND INSTITUTION LEVEL ONLY.
Individual researchers are never flagged or profiled.

Commands:
  ingest    Pull from arXiv, USPTO, and DARPA (SAM.gov)
  classify  Run Claude Haiku on unclassified items
  report    Generate Weekly Tech Watch markdown
  browse    Browse past reports and classified items
  demo      Self-contained walkthrough, no API key needed
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path


def _load_dotenv() -> None:
    env_file = Path(__file__).parent / ".env"
    if not env_file.exists():
        return
    for line in env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        key = key.strip()
        val = val.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = val


_load_dotenv()

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from config import (
    DB_PATH, DEFAULT_BROWSE_LIMIT, DEFAULT_REPORT_DAYS,
    FRAMING_NOTE, TIER_COLORS, DUAL_USE_TIERS,
)
from database import ScannerDB

console = Console()

_HEADER = Panel(
    f"[bold]Emerging Tech Horizon Scanner[/bold] — P39\n"
    f"[dim]{FRAMING_NOTE}[/dim]",
    border_style="dim",
    title="[dim]National Security Intelligence[/dim]",
)


@click.group()
def cli() -> None:
    """Emerging Tech Horizon Scanner — P39.

    \b
    Ingests arXiv preprints, USPTO patents, and DARPA solicitations.
    Claude classifies each item by technology domain, novelty, dual-use
    potential, and TRL. Generates Weekly Tech Watch markdown reports.
    Institution tracking reuses GhostTrace entity_resolver approach.

    \b
    Commands:
      ingest    Pull from arXiv, USPTO, DARPA (needs SAM_API_KEY for DARPA)
      classify  Run Claude on pending items (needs ANTHROPIC_API_KEY)
      report    Generate Weekly Tech Watch markdown report
      browse    Browse past reports or classified items
      demo      Self-contained walkthrough — no API keys needed
    """


# ── ingest ────────────────────────────────────────────────────────────────────

@cli.command()
@click.option("--db", "db_path", default=None, help="Override DB path.")
@click.option("--sources", "source_list",
              default="arxiv,patents,darpa",
              show_default=True,
              help="Comma-separated sources to ingest.")
def ingest(db_path: str | None, source_list: str) -> None:
    """Pull from arXiv, USPTO PatentsView, and DARPA (SAM.gov).

    arXiv and USPTO require no API key.
    DARPA requires SAM_API_KEY in your .env or environment.
    """
    console.print()
    console.print(_HEADER)

    sources = [s.strip().lower() for s in source_list.split(",")]
    db = ScannerDB(db_path or DB_PATH)
    total_added = 0

    if "arxiv" in sources:
        from sources.arxiv_client import fetch_all as arxiv_fetch
        console.print("\n[bold]arXiv — fetching defense-relevant preprints...[/bold]")
        items = arxiv_fetch()
        console.print(f"  Retrieved [cyan]{len(items)}[/cyan] papers.")
        added = sum(1 for i in items if db.add_item(i) is not None)
        console.print(f"  New: [green]{added}[/green] | Dupes skipped: [dim]{len(items) - added}[/dim]")
        total_added += added

    if "patents" in sources:
        from sources.patents_client import fetch_all as patents_fetch
        console.print("\n[bold]USPTO PatentsView — fetching recent defense patents...[/bold]")
        items = patents_fetch()
        console.print(f"  Retrieved [cyan]{len(items)}[/cyan] patents.")
        added = sum(1 for i in items if db.add_item(i) is not None)
        console.print(f"  New: [green]{added}[/green] | Dupes skipped: [dim]{len(items) - added}[/dim]")
        total_added += added

    if "darpa" in sources:
        from sources.darpa_client import fetch as darpa_fetch
        sam_key = os.environ.get("SAM_API_KEY", "")
        if not sam_key:
            console.print(
                "\n[yellow]DARPA:[/yellow] SAM_API_KEY not set — skipping DARPA solicitations.\n"
                "[dim]Add SAM_API_KEY to .env to enable DARPA ingestion.[/dim]"
            )
        else:
            console.print("\n[bold]DARPA via SAM.gov — fetching solicitations...[/bold]")
            items = darpa_fetch()
            console.print(f"  Retrieved [cyan]{len(items)}[/cyan] DARPA solicitations.")
            added = sum(1 for i in items if db.add_item(i) is not None)
            console.print(f"  New: [green]{added}[/green] | Dupes skipped: [dim]{len(items) - added}[/dim]")
            total_added += added

    _print_stats(db.get_stats())
    db.close()

    console.print(f"\n[bold green]{total_added}[/bold green] new items ingested total.")
    if total_added > 0:
        console.print("[dim]Run [bold]python main.py classify[/bold] to classify pending items.[/dim]")


# ── classify ──────────────────────────────────────────────────────────────────

@cli.command()
@click.option("--db", "db_path", default=None)
@click.option("--limit", default=20, show_default=True, type=int,
              help="Max items to classify per run.")
def classify(db_path: str | None, limit: int) -> None:
    """Classify pending items using Claude Haiku.

    Requires ANTHROPIC_API_KEY. Classifies by technology domain, dual-use
    tier, TRL, and novelty. Resolves institution names via entity resolver.
    """
    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise click.ClickException(
            "ANTHROPIC_API_KEY not set. Add it to .env or set the environment variable."
        )

    from claude_analyst import classify as claude_classify
    from entity_resolver import resolve_institution_list

    console.print()
    console.print(_HEADER)

    db = ScannerDB(db_path or DB_PATH)
    pending = db.get_pending_items(limit=limit)

    if not pending:
        console.print("[yellow]No pending items. Run [bold]python main.py ingest[/bold] first.[/yellow]")
        db.close()
        return

    console.print(f"\n[bold]Classifying {len(pending)} items with Claude Haiku...[/bold]")
    console.print("[dim]Framing: technology trend and institution level only.[/dim]\n")

    done = error = 0
    for item in pending:
        title_preview = item["title"][:70]
        console.print(f"  [{item['source']}] {title_preview}...")
        try:
            assessment = claude_classify(item)

            # Resolve institution names from both raw metadata and Claude extraction
            raw_insts = json.loads(item.get("raw_institutions") or "[]")
            claude_insts = assessment.get("institutions") or []
            all_inst_names = list(dict.fromkeys(raw_insts + claude_insts))
            canonical_insts = resolve_institution_list(all_inst_names)

            db.mark_classified(item["id"], assessment, canonical_insts)

            tier = assessment.get("dual_use_tier", "?")
            tier_color = TIER_COLORS.get(tier, "")
            console.print(
                f"    [{tier_color}]{tier}[/{tier_color}] | "
                f"TRL {assessment.get('trl')} | "
                f"Novelty {assessment.get('novelty_score')}/10 | "
                f"{assessment.get('tech_domain', 'Unknown')}"
            )
            done += 1
        except Exception as exc:
            console.print(f"    [red]error: {exc}[/red]")
            db.mark_error(item["id"])
            error += 1

    console.print(f"\n  Done: [green]{done}[/green] | Error: [red]{error}[/red]")
    _print_stats(db.get_stats())
    db.close()

    if done > 0:
        console.print("\n[dim]Run [bold]python main.py report[/bold] to generate the Tech Watch.[/dim]")


# ── report ────────────────────────────────────────────────────────────────────

@cli.command()
@click.option("--db", "db_path", default=None)
@click.option("--days", default=DEFAULT_REPORT_DAYS, show_default=True, type=int,
              help="Number of days to cover.")
@click.option("--domain", default=None, help="Filter by technology domain.")
@click.option("--tier", default=None,
              type=click.Choice(["CRITICAL", "HIGH", "MEDIUM", "LOW"]),
              help="Filter by dual-use tier.")
@click.option("--save/--no-save", default=True,
              help="Save report to reports/ directory.")
def report(db_path: str | None, days: int, domain: str | None,
           tier: str | None, save: bool) -> None:
    """Generate the Weekly Tech Watch markdown report.

    Aggregates classified items, groups by technology domain, and produces
    a structured markdown report stored in SQLite and (optionally) on disk.
    """
    from report_generator import generate, save_to_disk

    console.print()
    console.print(_HEADER)

    db = ScannerDB(db_path or DB_PATH)
    items = db.get_classified_items(domain=domain, tier=tier, days=days)

    if not items:
        console.print(
            f"[yellow]No classified items in the last {days} days.\n"
            "Run [bold]python main.py ingest[/bold] then [bold]python main.py classify[/bold].[/yellow]"
        )
        db.close()
        return

    console.print(f"\n[bold]Generating Weekly Tech Watch ({len(items)} items, last {days} days)...[/bold]")

    now = datetime.now(timezone.utc)
    title = f"Weekly Tech Watch — {now.strftime('%Y-%m-%d')}"
    period_start = (now.replace(hour=0, minute=0, second=0)
                    - __import__("datetime").timedelta(days=days)).isoformat()
    period_end = now.isoformat()

    markdown = generate(items, period_days=days)
    report_id = db.save_report(title, markdown, period_start, period_end, len(items))
    db.close()

    console.print(f"  Saved to database (report id={report_id})")

    if save:
        path = save_to_disk(markdown, title)
        console.print(f"  Written to [bold]{path}[/bold]")

    console.print()
    console.print(markdown[:3000] + ("\n...[truncated — see file for full report]" if len(markdown) > 3000 else ""))


# ── browse ────────────────────────────────────────────────────────────────────

@cli.command()
@click.option("--db", "db_path", default=None)
@click.option("--items", "show_items", is_flag=True, default=False,
              help="Browse classified items instead of reports.")
@click.option("--domain", default=None, help="Filter items by technology domain.")
@click.option("--tier", default=None,
              type=click.Choice(["CRITICAL", "HIGH", "MEDIUM", "LOW"]),
              help="Filter items by dual-use tier.")
@click.option("--days", default=None, type=int, help="Limit items to last N days.")
@click.option("--limit", default=DEFAULT_BROWSE_LIMIT, show_default=True, type=int)
@click.option("--report-id", default=None, type=int,
              help="Print the full body of a specific report.")
def browse(db_path: str | None, show_items: bool, domain: str | None,
           tier: str | None, days: int | None, limit: int, report_id: int | None) -> None:
    """Browse past reports and classified items.

    By default lists the most recent reports.
    Use --items to browse individual classified items.
    Use --report-id N to print the full body of report N.
    """
    console.print()
    console.print(_HEADER)

    db = ScannerDB(db_path or DB_PATH)

    if report_id is not None:
        body = db.get_report_body(report_id)
        db.close()
        if body is None:
            console.print(f"[red]Report {report_id} not found.[/red]")
        else:
            console.print()
            console.print(body)
        return

    if show_items:
        items = db.get_classified_items(domain=domain, tier=tier, days=days, limit=limit)
        db.close()
        _print_items_table(items)
    else:
        reports = db.get_reports(limit=limit)
        db.close()
        _print_reports_table(reports)


def _print_reports_table(reports: list[dict]) -> None:
    if not reports:
        console.print("[yellow]No reports yet. Run [bold]python main.py report[/bold].[/yellow]")
        return
    table = Table(title="Past Weekly Tech Watch Reports", show_lines=True)
    table.add_column("ID", style="dim", width=4)
    table.add_column("Title", style="bold")
    table.add_column("Items", justify="right")
    table.add_column("Generated", style="dim")
    for r in reports:
        table.add_row(
            str(r["id"]),
            r["title"],
            str(r.get("item_count") or 0),
            (r.get("generated_at") or "")[:16],
        )
    console.print()
    console.print(table)
    console.print("[dim]Use --report-id N to print the full report body.[/dim]")


def _print_items_table(items: list[dict]) -> None:
    if not items:
        console.print("[yellow]No classified items found.[/yellow]")
        return
    table = Table(title="Classified Tech Items", show_lines=True)
    table.add_column("ID", style="dim", width=5)
    table.add_column("Source", width=8)
    table.add_column("Tier", width=10)
    table.add_column("Domain", width=25)
    table.add_column("TRL", justify="right", width=5)
    table.add_column("N", justify="right", width=3)
    table.add_column("Title")

    for item in items:
        tier = item.get("dual_use_tier") or "?"
        color = TIER_COLORS.get(tier, "")
        tier_text = Text(tier, style=color)
        table.add_row(
            str(item["id"]),
            item.get("source", ""),
            tier_text,
            (item.get("tech_domain") or "")[:24],
            str(item.get("trl") or "?"),
            str(item.get("novelty_score") or "?"),
            item["title"][:60],
        )
    console.print()
    console.print(table)


def _print_stats(stats: dict) -> None:
    total = sum(stats.get(k, 0) for k in ("pending", "done", "error"))
    console.print(f"\n  DB — total: [cyan]{total}[/cyan]"
                  f" | pending: [yellow]{stats.get('pending', 0)}[/yellow]"
                  f" | done: [green]{stats.get('done', 0)}[/green]"
                  f" | error: [red]{stats.get('error', 0)}[/red]")
    if stats.get("tiers"):
        tier_parts = []
        for t in DUAL_USE_TIERS:
            n = stats["tiers"].get(t, 0)
            if n:
                tier_parts.append(f"[{TIER_COLORS[t]}]{t}[/{TIER_COLORS[t]}]: {n}")
        if tier_parts:
            console.print("  Tiers — " + " | ".join(tier_parts))


# ── demo ──────────────────────────────────────────────────────────────────────

@cli.command()
def demo() -> None:
    """Self-contained demo — no API keys needed.

    Seeds 14 pre-classified items spanning arXiv preprints, USPTO patents,
    and DARPA solicitations across 7 technology domains, then generates and
    displays a full Weekly Tech Watch report.
    """
    from seed_data import DEMO_SEEDS
    from report_generator import generate

    console.print()
    console.print(Panel(
        "[bold]Emerging Tech Horizon Scanner — Demo[/bold]\n"
        "arXiv + USPTO + DARPA → Claude classification → Weekly Tech Watch\n\n"
        f"[dim]{FRAMING_NOTE}[/dim]",
        border_style="blue",
        title="[bold]P39[/bold]",
    ))

    console.print("\n[bold underline]Step 1 — Seed item bank[/bold underline]")
    db = ScannerDB(":memory:")
    added = db.seed_demo(DEMO_SEEDS)
    console.print(f"  Seeded [cyan]{added}[/cyan] items across arXiv, USPTO, and DARPA.")
    console.print("  [dim](Pre-classified — no ANTHROPIC_API_KEY needed for demo)[/dim]")

    stats = db.get_stats()
    _print_stats(stats)

    console.print("\n[bold underline]Step 2 — Classified item browser[/bold underline]")
    items = db.get_classified_items(limit=50)
    _print_items_table(items)

    console.print("\n[bold underline]Step 3 — Weekly Tech Watch Report[/bold underline]")
    markdown = generate(items, period_days=DEFAULT_REPORT_DAYS)
    console.print()
    # Print a preview — full report is long
    preview_lines = markdown.splitlines()[:80]
    console.print("\n".join(preview_lines))
    if len(markdown.splitlines()) > 80:
        console.print(f"\n[dim]... ({len(markdown.splitlines()) - 80} more lines — "
                      "run [bold]python main.py report[/bold] for full output)[/dim]")

    console.print("\n[bold underline]Step 4 — Institution tracking[/bold underline]")
    from entity_resolver import resolve_institution_list
    all_insts: list[str] = []
    for item in items:
        insts = json.loads(item.get("canonical_institutions") or "[]")
        all_insts.extend(insts)
    canonical = resolve_institution_list(all_insts)
    console.print("  Canonical institutions tracked across all items:")
    for inst in canonical:
        count = all_insts.count(inst)
        console.print(f"    [cyan]{inst}[/cyan] — {count} item(s)")

    console.print()
    console.print(Panel(
        "Run [bold]python main.py ingest[/bold] to pull live arXiv + USPTO data.\n"
        "Run [bold]python main.py classify[/bold] (needs ANTHROPIC_API_KEY) to classify.\n"
        "Run [bold]python main.py report[/bold] to generate and save a full Tech Watch.\n"
        "Run [bold]python main.py browse --items[/bold] to explore classified items.",
        border_style="green",
        title="[bold]Next steps[/bold]",
    ))

    db.close()


if __name__ == "__main__":
    cli()
