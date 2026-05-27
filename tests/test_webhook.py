import hashlib
import hmac
import pytest
from fastapi.testclient import TestClient

from server.main import app
from server.webhook import verify_signature

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_config():
    """Reset webhook secret after each test to avoid config bleed."""
    import server.config as config
    original = config.GITHUB_WEBHOOK_SECRET
    yield
    config.GITHUB_WEBHOOK_SECRET = original


class TestWebhookSignature:
    def test_valid_signature(self):
        import server.config as config
        config.GITHUB_WEBHOOK_SECRET = "test_secret"

        body = b'{"action":"opened"}'
        mac = hmac.new(b"test_secret", body, hashlib.sha256)
        signature = f"sha256={mac.hexdigest()}"
        assert verify_signature(body, signature) is True

    def test_invalid_signature(self):
        import server.config as config
        config.GITHUB_WEBHOOK_SECRET = "test_secret"

        body = b'{"action":"opened"}'
        assert verify_signature(body, "sha256=wrong") is False


class TestHealthEndpoint:
    def test_health_check(self):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


class TestWebhookEndpoint:
    def test_ignores_non_pr_event(self):
        import server.config as config
        config.GITHUB_WEBHOOK_SECRET = ""
        response = client.post(
            "/webhook",
            json={"action": "created"},
            headers={"X-GitHub-Event": "issues"},
        )
        assert response.status_code == 200
        assert "Ignored event" in response.text

    def test_ignores_irrelevant_action(self):
        import server.config as config
        config.GITHUB_WEBHOOK_SECRET = ""
        response = client.post(
            "/webhook",
            json={"action": "closed"},
            headers={"X-GitHub-Event": "pull_request"},
        )
        assert response.status_code == 200
        assert "Ignored action" in response.text

    def test_requires_installation_id(self):
        import server.config as config
        config.GITHUB_WEBHOOK_SECRET = ""
        response = client.post(
            "/webhook",
            json={
                "action": "opened",
                "repository": {"full_name": "user/repo"},
                "pull_request": {"number": 1},
            },
            headers={"X-GitHub-Event": "pull_request"},
        )
        assert response.status_code == 400
