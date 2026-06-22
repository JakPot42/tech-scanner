"""Tests for source clients — all HTTP calls mocked."""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

import json
from unittest.mock import MagicMock, patch

import pytest


# ── arXiv client ─────────────────────────────────────────────────────────────

ARXIV_ATOM = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom"
      xmlns:arxiv="http://arxiv.org/schemas/atom">
  <entry>
    <id>https://arxiv.org/abs/2501.99999</id>
    <title>Hypersonic Boundary Layer Control via Plasma Actuators</title>
    <summary>We demonstrate plasma-actuated boundary layer control at Mach 6 reducing drag by 22%.</summary>
    <published>2026-01-10T00:00:00Z</published>
    <author>
      <name>Jane Doe</name>
      <arxiv:affiliation>NASA Ames Research Center</arxiv:affiliation>
    </author>
    <author>
      <name>John Smith</name>
      <arxiv:affiliation>Caltech</arxiv:affiliation>
    </author>
  </entry>
  <entry>
    <id>https://arxiv.org/abs/2501.88888</id>
    <title>Quantum Gyroscope for Navigation in GPS-Denied Environments</title>
    <summary>Atom-interferometric gyroscope achieving 1e-10 rad/s/sqrt(Hz) sensitivity.</summary>
    <published>2026-01-08T00:00:00Z</published>
    <author>
      <name>Alice Brown</name>
    </author>
  </entry>
</feed>"""


class TestArxivClient:
    def _mock_response(self):
        resp = MagicMock()
        resp.raise_for_status = MagicMock()
        resp.text = ARXIV_ATOM
        return resp

    def test_fetch_returns_items(self):
        with patch("requests.get", return_value=self._mock_response()):
            from sources.arxiv_client import fetch
            items = fetch("ti:hypersonic", max_results=5)
        assert len(items) == 2

    def test_item_has_required_fields(self):
        with patch("requests.get", return_value=self._mock_response()):
            from sources.arxiv_client import fetch
            items = fetch("ti:hypersonic")
        item = items[0]
        assert item["source"] == "arxiv"
        assert item["external_id"] == "2501.99999"
        assert "Hypersonic" in item["title"]
        assert item["abstract"]
        assert item["url"].startswith("https://arxiv.org")
        assert item["published_date"] == "2026-01-10"

    def test_extracts_affiliations(self):
        with patch("requests.get", return_value=self._mock_response()):
            from sources.arxiv_client import fetch
            items = fetch("ti:hypersonic")
        assert "NASA Ames Research Center" in items[0]["raw_institutions"]
        assert "Caltech" in items[0]["raw_institutions"]

    def test_no_affiliation_is_empty_list(self):
        with patch("requests.get", return_value=self._mock_response()):
            from sources.arxiv_client import fetch
            items = fetch("ti:quantum")
        assert items[1]["raw_institutions"] == []

    def test_network_error_returns_empty(self):
        with patch("requests.get", side_effect=Exception("timeout")):
            from sources.arxiv_client import fetch
            items = fetch("ti:hypersonic")
        assert items == []

    def test_fetch_all_deduplicates(self):
        with patch("requests.get", return_value=self._mock_response()):
            from sources.arxiv_client import fetch_all
            items = fetch_all()
        ids = [i["external_id"] for i in items]
        assert len(ids) == len(set(ids))

    def test_item_source_type(self):
        with patch("requests.get", return_value=self._mock_response()):
            from sources.arxiv_client import fetch
            items = fetch("ti:hypersonic")
        assert all(i["source"] == "arxiv" for i in items)


# ── PatentsView client ────────────────────────────────────────────────────────

PATENTS_JSON = {
    "patents": [
        {
            "patent_id": "US11999001",
            "patent_title": "Autonomous Drone Swarm Coordination in Contested Environments",
            "patent_abstract": "A distributed coordination framework enabling 64-agent UAV swarm operations without GPS.",
            "patent_date": "2026-01-15",
            "assignees": [{"assignee_organization": "Northrop Grumman Systems Corporation"}],
        },
        {
            "patent_id": "US11999002",
            "patent_title": "Neuromorphic Signal Classifier for ELINT Applications",
            "patent_abstract": "Spiking neural network chip for real-time electronic intelligence classification.",
            "patent_date": "2026-01-10",
            "assignees": [],
        },
    ]
}


class TestPatentsClient:
    def _mock_response(self):
        resp = MagicMock()
        resp.raise_for_status = MagicMock()
        resp.json = MagicMock(return_value=PATENTS_JSON)
        return resp

    def test_fetch_returns_items(self):
        with patch("requests.get", return_value=self._mock_response()):
            from sources.patents_client import fetch
            items = fetch("autonomous swarm")
        assert len(items) == 2

    def test_item_has_required_fields(self):
        with patch("requests.get", return_value=self._mock_response()):
            from sources.patents_client import fetch
            items = fetch("autonomous swarm")
        item = items[0]
        assert item["source"] == "patent"
        assert item["external_id"] == "US11999001"
        assert "Autonomous" in item["title"]
        assert "google.com/patent" in item["url"]

    def test_extracts_assignee(self):
        with patch("requests.get", return_value=self._mock_response()):
            from sources.patents_client import fetch
            items = fetch("autonomous swarm")
        assert "Northrop Grumman Systems Corporation" in items[0]["raw_institutions"]

    def test_empty_assignees_gives_empty_institutions(self):
        with patch("requests.get", return_value=self._mock_response()):
            from sources.patents_client import fetch
            items = fetch("neuromorphic")
        assert items[1]["raw_institutions"] == []

    def test_network_error_returns_empty(self):
        with patch("requests.get", side_effect=Exception("network")):
            from sources.patents_client import fetch
            items = fetch("hypersonic")
        assert items == []

    def test_fetch_all_deduplicates(self):
        with patch("requests.get", return_value=self._mock_response()):
            from sources.patents_client import fetch_all
            items = fetch_all()
        ids = [i["external_id"] for i in items]
        assert len(ids) == len(set(ids))


# ── DARPA client ──────────────────────────────────────────────────────────────

DARPA_JSON = {
    "opportunitiesData": [
        {
            "noticeId":       "BAA-DARPA-I2O-26-001",
            "solicitationNumber": "BAA-DARPA-I2O-26-001",
            "title":          "AI-Enabled Multi-Domain C2",
            "description":    "DARPA I2O seeks AI for multi-domain command and control.",
            "postedDate":     "2026-02-01T00:00:00Z",
            "subtierAgencyName": "DEFENSE ADVANCED RESEARCH PROJECTS AGENCY",
            "uiLink":         "https://sam.gov/opp/test",
        },
        {
            "noticeId":       "OTHER-AGENCY-001",
            "solicitationNumber": "OTHER-001",
            "title":          "Army Logistics Software",
            "description":    "Army procurement of logistics software.",
            "postedDate":     "2026-02-01T00:00:00Z",
            "subtierAgencyName": "ARMY",
            "uiLink":         "https://sam.gov/opp/other",
        },
    ]
}


class TestDarpaClient:
    def _mock_response(self):
        resp = MagicMock()
        resp.raise_for_status = MagicMock()
        resp.json = MagicMock(return_value=DARPA_JSON)
        return resp

    def test_filters_darpa_only(self):
        with patch("requests.get", return_value=self._mock_response()):
            with patch.dict("os.environ", {"SAM_API_KEY": "test-key"}):
                from sources.darpa_client import fetch
                items = fetch()
        assert len(items) == 1
        assert "DARPA" in items[0]["title"] or "C2" in items[0]["title"]

    def test_item_has_required_fields(self):
        with patch("requests.get", return_value=self._mock_response()):
            with patch.dict("os.environ", {"SAM_API_KEY": "test-key"}):
                from sources.darpa_client import fetch
                items = fetch()
        item = items[0]
        assert item["source"] == "darpa"
        assert item["external_id"] == "BAA-DARPA-I2O-26-001"
        assert item["raw_institutions"] == ["DARPA"]

    def test_no_api_key_returns_empty(self):
        env = {k: v for k, v in __import__("os").environ.items() if k != "SAM_API_KEY"}
        with patch.dict("os.environ", env, clear=True):
            from sources.darpa_client import fetch
            items = fetch()
        assert items == []

    def test_network_error_returns_empty(self):
        with patch("requests.get", side_effect=Exception("network")):
            with patch.dict("os.environ", {"SAM_API_KEY": "test-key"}):
                from sources.darpa_client import fetch
                items = fetch()
        assert items == []
