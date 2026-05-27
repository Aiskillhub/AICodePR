import pytest
from server.sanitizer import sanitize_diff, should_ignore_file, split_diff_by_file


class TestSanitizer:
    def test_redact_api_key(self):
        diff = 'api_key = "sk-abcdefghijklmnop1234567890"'
        result = sanitize_diff(diff)
        assert "sk-abcdefghijklmnop" not in result
        assert "REDACTED" in result

    def test_redact_github_token(self):
        diff = "export GITHUB_TOKEN=ghp_abc123def456ghi789jkl012mno345pqr678stu"
        result = sanitize_diff(diff)
        assert "ghp_abc" not in result
        assert "REDACTED" in result

    def test_redact_bearer_token(self):
        diff = "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.xxx"
        result = sanitize_diff(diff)
        assert "eyJhbG" not in result
        assert "REDACTED" in result

    def test_redact_password(self):
        diff = 'password = "supersecret123"'
        result = sanitize_diff(diff)
        assert "supersecret123" not in result
        assert "REDACTED" in result

    def test_redact_jdbc_url(self):
        diff = "jdbc:mysql://localhost/db?user=admin&password=secretpass"
        result = sanitize_diff(diff)
        assert "secretpass" not in result
        assert "REDACTED" in result

    def test_preserve_normal_code(self):
        diff = "def foo():\n    x = 1 + 2\n    return x"
        result = sanitize_diff(diff)
        assert result == diff


class TestShouldIgnoreFile:
    def test_ignore_lock_files(self):
        assert should_ignore_file("package-lock.json")
        assert should_ignore_file("yarn.lock")
        assert should_ignore_file("Cargo.lock")
        assert should_ignore_file("pnpm-lock.yaml")

    def test_ignore_minified_files(self):
        assert should_ignore_file("bundle.min.js")
        assert should_ignore_file("style.min.css")

    def test_ignore_images(self):
        assert should_ignore_file("logo.png")
        assert should_ignore_file("icon.svg")
        assert should_ignore_file("font.woff2")

    def test_allow_source_files(self):
        assert not should_ignore_file("src/app.py")
        assert not should_ignore_file("components/Button.tsx")
        assert not should_ignore_file("main.go")


class TestSplitDiffByFile:
    def test_small_diff_returns_single_chunk(self):
        diff = "diff --git a/a.py b/a.py\n+print('hello')\n"
        chunks = split_diff_by_file(diff, 8000)
        assert len(chunks) == 1

    def test_large_diff_splits(self):
        large_diff = "diff --git a/a.py b/a.py\n" + "+x = 1\n" * 3000
        chunks = split_diff_by_file(large_diff, 2000)
        assert len(chunks) > 1

    def test_empty_diff(self):
        chunks = split_diff_by_file("", 8000)
        assert chunks == []
