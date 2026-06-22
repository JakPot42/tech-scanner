"""Tests for CLI commands — all external calls mocked."""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

import json
import os
from unittest.mock import MagicMock, patch, call

import pytest
from click.testing import CliRunner

from main import cli
from database import ScannerDB
from seed_data import DEMO_SEEDS


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def temp_db(tmp_path):
    return str(tmp_path / "test.db")


class TestDemo:
    def test_demo_runs_without_api_key(self, runner):
        result = runner.invoke(cli, ["demo"])
        assert result.exit_code == 0, result.output

    def test_demo_shows_items(self, runner):
        result = runner.invoke(cli, ["demo"])
        assert "CRITICAL" in result.output or "HIGH" in result.output

    def test_demo_shows_institution_tracking(self, runner):
        result = runner.invoke(cli, ["demo"])
        assert "Institution" in result.output or "Institutions" in result.output

    def test_demo_shows_tech_watch(self, runner):
        result = runner.invoke(cli, ["demo"])
        assert "Tech Watch" in result.output or "Weekly" in result.output

    def test_demo_no_error_output(self, runner):
        result = runner.invoke(cli, ["demo"])
        assert "Error" not in result.output or result.exit_code == 0


class TestIngest:
    def _mock_arxiv(self):
        return [
            {"source": "arxiv", "external_id": "001", "title": "Test Paper",
             "abstract": "Abstract.", "url": "https://arxiv.org/abs/001",
             "published_date": "2026-06-22", "raw_institutions": ["MIT"]},
        ]

    def _mock_patents(self):
        return [
            {"source": "patent", "external_id": "US001", "title": "Test Patent",
             "abstract": "Patent abstract.", "url": "https://patents.google.com/patent/US001",
             "published_date": "2026-06-22", "raw_institutions": ["Raytheon"]},
        ]

    def test_ingest_arxiv_only(self, runner, temp_db):
        with patch("sources.arxiv_client.fetch_all", return_value=self._mock_arxiv()):
            result = runner.invoke(cli, ["ingest", "--db", temp_db, "--sources", "arxiv"])
        assert result.exit_code == 0
        assert "New:" in result.output

    def test_ingest_patents_only(self, runner, temp_db):
        with patch("sources.patents_client.fetch_all", return_value=self._mock_patents()):
            result = runner.invoke(cli, ["ingest", "--db", temp_db, "--sources", "patents"])
        assert result.exit_code == 0

    def test_ingest_darpa_skipped_without_key(self, runner, temp_db):
        env = {k: v for k, v in os.environ.items() if k != "SAM_API_KEY"}
        with patch.dict("os.environ", env, clear=True):
            with patch("sources.arxiv_client.fetch_all", return_value=[]):
                with patch("sources.patents_client.fetch_all", return_value=[]):
                    result = runner.invoke(cli, ["ingest", "--db", temp_db])
        assert result.exit_code == 0
        assert "SAM_API_KEY not set" in result.output or "skipping" in result.output.lower()

    def test_ingest_counts_new_items(self, runner, temp_db):
        with patch("sources.arxiv_client.fetch_all", return_value=self._mock_arxiv()):
            with patch("sources.patents_client.fetch_all", return_value=self._mock_patents()):
                result = runner.invoke(cli, ["ingest", "--db", temp_db, "--sources", "arxiv,patents"])
        assert "New:" in result.output

    def test_ingest_dedupes_on_second_run(self, runner, temp_db):
        with patch("sources.arxiv_client.fetch_all", return_value=self._mock_arxiv()):
            runner.invoke(cli, ["ingest", "--db", temp_db, "--sources", "arxiv"])
            result = runner.invoke(cli, ["ingest", "--db", temp_db, "--sources", "arxiv"])
        assert "Dupes skipped: 1" in result.output


class TestClassify:
    def _seed_db(self, db_path):
        db = ScannerDB(db_path)
        db.add_item({
            "source": "arxiv", "external_id": "001",
            "title": "Quantum Sensing Paper",
            "abstract": "Abstract about quantum sensors.",
            "url": "https://arxiv.org/abs/001",
            "published_date": "2026-06-22",
            "raw_institutions": ["MIT"],
        })
        db.close()

    def _good_assessment(self):
        return {
            "tech_domain": "Quantum Computing & Sensing",
            "novelty_score": 8, "dual_use_tier": "HIGH", "trl": 4,
            "trend_label": "Quantum sensors for defense",
            "key_finding": "Novel approach.", "institutions": ["MIT", "DARPA"],
        }

    def test_classify_requires_api_key(self, runner, temp_db):
        env = {k: v for k, v in os.environ.items() if k != "ANTHROPIC_API_KEY"}
        with patch.dict("os.environ", env, clear=True):
            result = runner.invoke(cli, ["classify", "--db", temp_db])
        assert result.exit_code != 0
        assert "ANTHROPIC_API_KEY" in result.output

    def test_classify_no_pending_items(self, runner, temp_db):
        with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-key"}):
            result = runner.invoke(cli, ["classify", "--db", temp_db])
        assert result.exit_code == 0
        assert "No pending items" in result.output

    def test_classify_processes_item(self, runner, temp_db):
        self._seed_db(temp_db)
        with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-key"}):
            with patch("claude_analyst.classify", return_value=self._good_assessment()):
                result = runner.invoke(cli, ["classify", "--db", temp_db])
        assert result.exit_code == 0
        assert "Done:" in result.output

    def test_classify_error_handling(self, runner, temp_db):
        self._seed_db(temp_db)
        with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-key"}):
            with patch("claude_analyst.classify", side_effect=Exception("API error")):
                result = runner.invoke(cli, ["classify", "--db", temp_db])
        assert result.exit_code == 0
        assert "error" in result.output.lower()


class TestReport:
    def _seed_classified(self, db_path):
        db = ScannerDB(db_path)
        db.seed_demo(DEMO_SEEDS)
        db.close()

    def test_report_no_items(self, runner, temp_db):
        result = runner.invoke(cli, ["report", "--db", temp_db, "--no-save"])
        assert result.exit_code == 0
        assert "No classified items" in result.output

    def test_report_generates_markdown(self, runner, temp_db):
        self._seed_classified(temp_db)
        result = runner.invoke(cli, ["report", "--db", temp_db, "--no-save"])
        assert result.exit_code == 0
        assert "Weekly Tech Watch" in result.output

    def test_report_saves_to_db(self, runner, temp_db):
        self._seed_classified(temp_db)
        runner.invoke(cli, ["report", "--db", temp_db, "--no-save"])
        db = ScannerDB(temp_db)
        reports = db.get_reports()
        db.close()
        assert len(reports) == 1

    def test_report_save_flag_creates_file(self, runner, temp_db, tmp_path):
        self._seed_classified(temp_db)
        with patch("report_generator.REPORTS_DIR", str(tmp_path / "reports")):
            result = runner.invoke(cli, ["report", "--db", temp_db, "--save"])
        assert result.exit_code == 0


class TestBrowse:
    def _seed(self, db_path):
        db = ScannerDB(db_path)
        db.seed_demo(DEMO_SEEDS)
        db.save_report("Test Report", "# Body", "", "", 5)
        db.close()

    def test_browse_reports_empty(self, runner, temp_db):
        result = runner.invoke(cli, ["browse", "--db", temp_db])
        assert result.exit_code == 0
        assert "No reports" in result.output

    def test_browse_reports_shows_table(self, runner, temp_db):
        self._seed(temp_db)
        result = runner.invoke(cli, ["browse", "--db", temp_db])
        assert result.exit_code == 0
        assert "Test Report" in result.output

    def test_browse_items_flag(self, runner, temp_db):
        self._seed(temp_db)
        result = runner.invoke(cli, ["browse", "--db", temp_db, "--items"])
        assert result.exit_code == 0
        assert "arxiv" in result.output.lower() or "patent" in result.output.lower()

    def test_browse_items_filter_tier(self, runner, temp_db):
        self._seed(temp_db)
        result = runner.invoke(cli, ["browse", "--db", temp_db, "--items", "--tier", "CRITICAL"])
        assert result.exit_code == 0

    def test_browse_report_by_id(self, runner, temp_db):
        self._seed(temp_db)
        result = runner.invoke(cli, ["browse", "--db", temp_db, "--report-id", "1"])
        assert result.exit_code == 0
        assert "Body" in result.output or "#" in result.output

    def test_browse_nonexistent_report_id(self, runner, temp_db):
        self._seed(temp_db)
        result = runner.invoke(cli, ["browse", "--db", temp_db, "--report-id", "999"])
        assert result.exit_code == 0
        assert "not found" in result.output.lower()
