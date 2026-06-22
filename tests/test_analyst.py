"""Tests for claude_analyst.py — Anthropic API fully mocked."""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

import json
from unittest.mock import MagicMock, patch

import pytest


def _make_mock_client(response_text: str):
    """Build a mock anthropic.Anthropic that returns response_text."""
    content = MagicMock()
    content.text = response_text

    msg = MagicMock()
    msg.content = [content]

    client = MagicMock()
    client.messages.create = MagicMock(return_value=msg)
    return client


GOOD_RESPONSE = json.dumps({
    "tech_domain": "Hypersonics & Advanced Propulsion",
    "novelty_score": 7,
    "dual_use_tier": "HIGH",
    "trl": 4,
    "trend_label": "Scramjet boundary layer control for hypersonic cruise",
    "key_finding": "Plasma actuators reducing drag at Mach 6 could extend scramjet range by 15%.",
    "institutions": ["NASA Ames Research Center", "Caltech"],
})


class TestClaudeAnalyst:
    def _item(self, source="arxiv", title="Test hypersonic paper", abstract="Test abstract"):
        return {
            "source": source,
            "external_id": "2501.99999",
            "title": title,
            "abstract": abstract,
            "raw_institutions": ["NASA", "Caltech"],
        }

    def test_classify_returns_dict(self):
        with patch("anthropic.Anthropic", return_value=_make_mock_client(GOOD_RESPONSE)):
            import claude_analyst
            claude_analyst._CLIENT = None
            with patch.object(claude_analyst, "_client", return_value=_make_mock_client(GOOD_RESPONSE)):
                result = claude_analyst.classify(self._item())
        assert isinstance(result, dict)

    def test_classify_has_required_fields(self):
        mock_c = _make_mock_client(GOOD_RESPONSE)
        with patch("claude_analyst._client", return_value=mock_c):
            from claude_analyst import classify
            result = classify(self._item())
        assert "tech_domain" in result
        assert "novelty_score" in result
        assert "dual_use_tier" in result
        assert "trl" in result
        assert "trend_label" in result
        assert "key_finding" in result
        assert "institutions" in result

    def test_novelty_score_clamped(self):
        resp = json.dumps({**json.loads(GOOD_RESPONSE), "novelty_score": 99})
        mock_c = _make_mock_client(resp)
        with patch("claude_analyst._client", return_value=mock_c):
            from claude_analyst import classify
            result = classify(self._item())
        assert result["novelty_score"] == 10

    def test_trl_clamped_low(self):
        resp = json.dumps({**json.loads(GOOD_RESPONSE), "trl": 0})
        mock_c = _make_mock_client(resp)
        with patch("claude_analyst._client", return_value=mock_c):
            from claude_analyst import classify
            result = classify(self._item())
        assert result["trl"] == 1

    def test_invalid_tier_defaults_medium(self):
        resp = json.dumps({**json.loads(GOOD_RESPONSE), "dual_use_tier": "EXTREME"})
        mock_c = _make_mock_client(resp)
        with patch("claude_analyst._client", return_value=mock_c):
            from claude_analyst import classify
            result = classify(self._item())
        assert result["dual_use_tier"] == "MEDIUM"

    def test_strips_markdown_fences(self):
        fenced = "```json\n" + GOOD_RESPONSE + "\n```"
        mock_c = _make_mock_client(fenced)
        with patch("claude_analyst._client", return_value=mock_c):
            from claude_analyst import classify
            result = classify(self._item())
        assert result["novelty_score"] == 7

    def test_invalid_domain_defaults(self):
        from config import TECH_DOMAINS
        resp = json.dumps({**json.loads(GOOD_RESPONSE), "tech_domain": "Alien Technology"})
        mock_c = _make_mock_client(resp)
        with patch("claude_analyst._client", return_value=mock_c):
            from claude_analyst import classify
            result = classify(self._item())
        assert result["tech_domain"] == TECH_DOMAINS[0]

    def test_patent_source_label(self):
        mock_c = _make_mock_client(GOOD_RESPONSE)
        with patch("claude_analyst._client", return_value=mock_c):
            from claude_analyst import classify
            result = classify(self._item(source="patent"))
        assert result["trl"] >= 1  # sanity

    def test_darpa_source_label(self):
        mock_c = _make_mock_client(GOOD_RESPONSE)
        with patch("claude_analyst._client", return_value=mock_c):
            from claude_analyst import classify
            result = classify(self._item(source="darpa"))
        assert result["dual_use_tier"] in ("LOW", "MEDIUM", "HIGH", "CRITICAL")

    def test_institutions_list_returned(self):
        mock_c = _make_mock_client(GOOD_RESPONSE)
        with patch("claude_analyst._client", return_value=mock_c):
            from claude_analyst import classify
            result = classify(self._item())
        assert isinstance(result["institutions"], list)
        assert "NASA Ames Research Center" in result["institutions"]
