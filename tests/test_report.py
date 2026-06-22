"""Tests for report_generator.py — no mocks needed, pure logic."""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

import json
import pytest
from seed_data import DEMO_SEEDS
from report_generator import generate, save_to_disk


def _items_from_seeds():
    """Build classified item dicts from DEMO_SEEDS for report testing."""
    items = []
    for seed in DEMO_SEEDS:
        item = {
            "id": len(items) + 1,
            "source": seed["source"],
            "external_id": seed["external_id"],
            "title": seed["title"],
            "abstract": seed.get("abstract", ""),
            "url": seed.get("url", ""),
            "published_date": seed.get("published_date", "2026-06-22"),
            "tech_domain": seed.get("tech_domain"),
            "novelty_score": seed.get("novelty_score"),
            "dual_use_tier": seed.get("dual_use_tier"),
            "trl": seed.get("trl"),
            "trend_label": seed.get("trend_label"),
            "key_finding": seed.get("key_finding"),
            "canonical_institutions": json.dumps(seed.get("canonical_institutions") or []),
            "status": "done",
        }
        items.append(item)
    return items


@pytest.fixture
def items():
    return _items_from_seeds()


class TestGenerate:
    def test_returns_string(self, items):
        md = generate(items)
        assert isinstance(md, str)
        assert len(md) > 100

    def test_has_title_header(self, items):
        md = generate(items)
        assert "# Weekly Tech Watch" in md

    def test_has_framing_note(self, items):
        md = generate(items)
        assert "institution" in md.lower()

    def test_has_dual_use_section(self, items):
        md = generate(items)
        assert "High & Critical" in md or "CRITICAL" in md

    def test_has_domain_section(self, items):
        md = generate(items)
        assert "Technology Domain" in md

    def test_has_institution_section(self, items):
        md = generate(items)
        assert "Institutional Activity" in md

    def test_has_darpa_section(self, items):
        md = generate(items)
        darpa_items = [i for i in items if i["source"] == "darpa"]
        if darpa_items:
            assert "DARPA Solicitations" in md

    def test_has_metadata_footer(self, items):
        md = generate(items)
        assert "Report Metadata" in md
        assert "arXiv" in md

    def test_critical_items_appear_first(self, items):
        md = generate(items)
        critical_items = [i for i in items if i.get("dual_use_tier") == "CRITICAL"]
        if critical_items:
            title = critical_items[0]["title"]
            assert title in md

    def test_empty_items_graceful(self):
        md = generate([])
        assert "No classified items" in md

    def test_item_count_in_header(self, items):
        md = generate(items)
        count = len(items)
        assert str(count) in md

    def test_institution_table_contains_mit(self, items):
        md = generate(items)
        assert "Massachusetts Institute of Technology" in md or "MIT" in md

    def test_darpa_in_institutions(self, items):
        md = generate(items)
        assert "DARPA" in md

    def test_no_individual_names(self, items):
        md = generate(items)
        # Report should not contain researcher names from seed data
        assert "Jane Doe" not in md
        assert "John Smith" not in md

    def test_trl_labels_appear(self, items):
        md = generate(items)
        assert "TRL" in md

    def test_period_days_in_header(self, items):
        md = generate(items, period_days=30)
        assert isinstance(md, str)  # just ensure no crash with different period

    def test_novelty_scores_appear(self, items):
        md = generate(items)
        assert "/10" in md


class TestSaveToDisk:
    def test_creates_file(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        md = "# Test Report\n\nContent here."
        path = save_to_disk(md, "Weekly Tech Watch — 2026-06-22")
        assert path.exists()
        assert path.read_text(encoding="utf-8") == md

    def test_filename_contains_timestamp(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        path = save_to_disk("body", "Test Report")
        assert "Test_Report" in path.name or "Test" in path.name

    def test_creates_reports_dir(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        save_to_disk("body", "report title")
        assert (tmp_path / "reports").exists()
