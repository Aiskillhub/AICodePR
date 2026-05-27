import hashlib
import hmac
import logging
from typing import Optional

from fastapi import APIRouter, Request, Response, BackgroundTasks

from server import config
from server.github_client import get_installation_client, get_pr_diff, post_review
from server.sanitizer import sanitize_diff, split_diff_by_file
from server.reviewer import review_diff
from server.schemas import ReviewResult, Finding

logger = logging.getLogger(__name__)
router = APIRouter()


def verify_signature(payload: bytes, signature: str) -> bool:
    """Verify GitHub webhook HMAC-SHA256 signature."""
    if not config.GITHUB_WEBHOOK_SECRET:
        logger.warning("Webhook secret not configured, skipping verification")
        return True

    mac = hmac.new(
        config.GITHUB_WEBHOOK_SECRET.encode(),
        payload,
        hashlib.sha256,
    )
    expected = f"sha256={mac.hexdigest()}"
    return hmac.compare_digest(expected, signature)


@router.post("/webhook")
async def github_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
) -> Response:
    """Receive GitHub pull_request webhook events."""
    body = await request.body()

    signature = request.headers.get("X-Hub-Signature-256", "")
    if not verify_signature(body, signature):
        return Response(status_code=401, content="Invalid signature")

    event_type = request.headers.get("X-GitHub-Event", "")
    if event_type != "pull_request":
        return Response(status_code=200, content=f"Ignored event: {event_type}")

    payload = await request.json()
    action = payload.get("action", "")

    if action not in ("opened", "synchronize", "reopened"):
        return Response(status_code=200, content=f"Ignored action: {action}")

    installation_id = payload.get("installation", {}).get("id")
    if not installation_id:
        return Response(status_code=400, content="Missing installation id")

    repo_name = payload["repository"]["full_name"]
    pr_number = payload["pull_request"]["number"]

    logger.info(f"Queuing review for {repo_name}#{pr_number}")
    background_tasks.add_task(
        run_review, installation_id, repo_name, pr_number
    )

    return Response(status_code=200, content="Review queued")


async def run_review(installation_id: int, repo_name: str, pr_number: int):
    """Fetch diff, run AI review, and post results. Runs in background."""
    try:
        client = get_installation_client(installation_id)
        repo = client.get_repo(repo_name)
        pr = repo.get_pull(pr_number)

        diff_text = get_pr_diff(repo, pr_number)
        if not diff_text.strip():
            logger.info(f"Empty diff for {repo_name}#{pr_number}")
            return

        clean_diff = sanitize_diff(diff_text)
        chunks = split_diff_by_file(clean_diff, config.MAX_DIFF_CHARS)

        all_findings: list[Finding] = []
        for chunk in chunks:
            result = await review_diff(chunk)
            all_findings.extend(result.findings)

        combined = ReviewResult(
            summary=f"Reviewed {len(chunks)} file(s), {len(all_findings)} issue(s) found.",
            findings=all_findings,
        )

        post_review(
            pr,
            combined.summary,
            [f.model_dump() for f in combined.findings],
        )

        logger.info(f"Review complete for {repo_name}#{pr_number}: {len(all_findings)} findings")

    except Exception as e:
        logger.error(f"Review failed for {repo_name}#{pr_number}: {e}", exc_info=True)
