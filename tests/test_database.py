"""Tests for ScannerDB — in-memory SQLite, no mocks needed."""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

import json
import pytest

from database import ScannerDB
from seed_data import DEMO_SEEDS


def _item(source="arxiv", ext_id="arxiv:001", title="Test Paper"):
    return {
        "source": source,
        "external_id": ext_id,
        "title": title,
        "abstract": "A test abstract.",
        "url": "https://arxiv.org/abs/001",
        "published_date": "2026-06-22",
        "raw_institutions": ["MIT", "DARPA"],
    }


def _assessment():
    return {
        "tech_domain": "Quantum Computing & Sensing",
        "novelty_score": 8,
        "dual_use_tier": "HIGH",
        "trl": 4,
        "trend_label": "Quantum sensing for navigation",
        "key_finding": "Novel quantum gyroscope reduces inertial nav drift.",
    }


@pytest.fixture
def db():
    d = ScannerDB(":memory:")
    yield d
    d.close()


class TestAddItem:
    def test_add_returns_id(self, db):
        item_id = db.add_item(_item())
        assert isinstance(item_id, int)
        assert item_id > 0

    def test_duplicate_returns_none(self, db):
        db.add_item(_item())
        result = db.add_item(_item())
        assert result is None

    def test_external_id_exists(self, db):
        db.add_item(_item())
        assert db.external_id_exists("arxiv", "arxiv:001")
        assert not db.external_id_exists("arxiv", "nonexistent")

    def test_item_shows_in_pending(self, db):
        db.add_item(_item())
        pending = db.get_pending_items()
        assert len(pending) == 1
        assert pending[0]["title"] == "Test Paper"

    def test_multiple_items_different_ids(self, db):
        id1 = db.add_item(_item(ext_id="001"))
        id2 = db.add_item(_item(ext_id="002"))
        assert id1 != id2


class TestMarkClassified:
    def test_moves_to_done(self, db):
        item_id = db.add_item(_item())
        db.mark_classified(item_id, _assessment(), ["MIT", "DARPA"])
        done = db.get_classified_items()
        assert len(done) == 1

    def test_pending_empty_after_classify(self, db):
        item_id = db.add_item(_item())
        db.mark_classified(item_id, _assessment(), ["MIT"])
        assert db.get_pending_items() == []

    def test_canonical_institutions_stored(self, db):
        item_id = db.add_item(_item())
        db.mark_classified(item_id, _assessment(), ["MIT", "DARPA"])
        items = db.get_classified_items()
        insts = json.loads(items[0]["canonical_institutions"])
        assert "MIT" in insts
        assert "DARPA" in insts

    def test_assessment_fields_stored(self, db):
        item_id = db.add_item(_item())
        db.mark_classified(item_id, _assessment(), [])
        items = db.get_classified_items()
        row = items[0]
        assert row["tech_domain"] == "Quantum Computing & Sensing"
        assert row["novelty_score"] == 8
        assert row["dual_use_tier"] == "HIGH"
        assert row["trl"] == 4

    def test_mark_error(self, db):
        item_id = db.add_item(_item())
        db.mark_error(item_id)
        pending = db.get_pending_items()
        done = db.get_classified_items()
        assert len(pending) == 0
        assert len(done) == 0


class TestGetClassifiedItems:
    def _seed_two(self, db):
        id1 = db.add_item(_item(ext_id="001", source="arxiv"))
        id2 = db.add_item(_item(ext_id="002", source="patent"))
        db.mark_classified(id1, {**_assessment(), "dual_use_tier": "HIGH"}, ["MIT"])
        db.mark_classified(id2, {**_assessment(), "dual_use_tier": "CRITICAL",
                                  "tech_domain": "Hypersonics & Advanced Propulsion"}, ["Raytheon"])

    def test_returns_all_done(self, db):
        self._seed_two(db)
        items = db.get_classified_items()
        assert len(items) == 2

    def test_filter_by_tier(self, db):
        self._seed_two(db)
        critical = db.get_classified_items(tier="CRITICAL")
        assert len(critical) == 1
        assert critical[0]["dual_use_tier"] == "CRITICAL"

    def test_filter_by_domain(self, db):
        self._seed_two(db)
        hypersonics = db.get_classified_items(domain="Hypersonics & Advanced Propulsion")
        assert len(hypersonics) == 1

    def test_limit_respected(self, db):
        for i in range(5):
            item_id = db.add_item(_item(ext_id=f"item{i}"))
            db.mark_classified(item_id, _assessment(), [])
        items = db.get_classified_items(limit=3)
        assert len(items) <= 3


class TestStats:
    def test_stats_keys(self, db):
        db.add_item(_item(ext_id="001"))
        stats = db.get_stats()
        assert "pending" in stats

    def test_stats_after_classify(self, db):
        item_id = db.add_item(_item())
        db.mark_classified(item_id, _assessment(), [])
        stats = db.get_stats()
        assert stats.get("done", 0) == 1
        assert stats.get("pending", 0) == 0

    def test_tier_counts_in_stats(self, db):
        item_id = db.add_item(_item())
        db.mark_classified(item_id, _assessment(), [])
        stats = db.get_stats()
        assert "tiers" in stats
        assert stats["tiers"].get("HIGH") == 1


class TestReports:
    def test_save_and_retrieve(self, db):
        report_id = db.save_report(
            "Weekly Tech Watch — 2026-06-22",
            "# Report body",
            "2026-06-15T00:00:00",
            "2026-06-22T00:00:00",
            10,
        )
        assert report_id > 0
        body = db.get_report_body(report_id)
        assert body == "# Report body"

    def test_get_reports_list(self, db):
        db.save_report("Report 1", "body1", "", "", 5)
        db.save_report("Report 2", "body2", "", "", 3)
        reports = db.get_reports()
        assert len(reports) == 2

    def test_missing_report_returns_none(self, db):
        assert db.get_report_body(999) is None


class TestSeedDemo:
    def test_seeds_all_items(self, db):
        added = db.seed_demo(DEMO_SEEDS)
        assert added == len(DEMO_SEEDS)

    def test_seeded_items_are_done(self, db):
        db.seed_demo(DEMO_SEEDS)
        done = db.get_classified_items()
        assert len(done) == len(DEMO_SEEDS)

    def test_no_pending_after_seed(self, db):
        db.seed_demo(DEMO_SEEDS)
        assert db.get_pending_items() == []

    def test_idempotent_seed(self, db):
        db.seed_demo(DEMO_SEEDS)
        added_again = db.seed_demo(DEMO_SEEDS)
        assert added_again == 0
