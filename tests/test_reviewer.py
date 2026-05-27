import json
import pytest
from server.schemas import Finding, ReviewResult
from server.reviewer import _parse_ai_response


class TestSchemas:
    def test_valid_finding(self):
        f = Finding(
            file_path="src/app.py",
            line_number=42,
            severity="high",
            title="SQL injection",
            description="Unsafe query construction",
        )
        assert f.file_path == "src/app.py"
        assert f.line_number == 42
        assert f.severity == "high"

    def test_invalid_line_number_raises(self):
        with pytest.raises(Exception):
            Finding(
                file_path="src/app.py",
                line_number=0,
                severity="high",
                title="Test",
                description="Test",
            )

    def test_invalid_severity_raises(self):
        with pytest.raises(Exception):
            Finding(
                file_path="src/app.py",
                line_number=1,
                severity="unknown",
                title="Test",
                description="Test",
            )

    def test_empty_findings_valid(self):
        result = ReviewResult(summary="All good")
        assert result.findings == []


class TestParseAIResponse:
    def test_parse_valid_json(self):
        response = json.dumps({
            "summary": "Found 2 issues",
            "findings": [
                {
                    "file_path": "src/a.py",
                    "line_number": 10,
                    "severity": "high",
                    "title": "SQL injection",
                    "description": "Bad query",
                    "suggestion": "Use params",
                }
            ],
        })
        result = _parse_ai_response(response)
        assert result.summary == "Found 2 issues"
        assert len(result.findings) == 1
        assert result.findings[0].title == "SQL injection"

    def test_parse_json_in_markdown(self):
        response = '```json\n{"summary": "ok", "findings": []}\n```'
        result = _parse_ai_response(response)
        assert result.summary == "ok"

    def test_parse_no_findings(self):
        response = '{"summary": "LGTM", "findings": []}'
        result = _parse_ai_response(response)
        assert result.summary == "LGTM"
        assert result.findings == []

    def test_parse_invalid_json_returns_safe_default(self):
        result = _parse_ai_response("not json at all {{")
        assert "unavailable" in result.summary.lower()

    def test_parse_missing_key_returns_safe_default(self):
        result = _parse_ai_response('{"wrong_key": "oops"}')
        assert "unavailable" in result.summary.lower()
