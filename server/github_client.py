import logging
from github import Github, GithubIntegration
from github.PullRequest import PullRequest
from github.Repository import Repository

from server.config import GITHUB_APP_ID, GITHUB_PRIVATE_KEY

logger = logging.getLogger(__name__)


def get_installation_client(installation_id: int) -> Github:
    """Get an authenticated PyGithub client for a specific installation."""
    integration = GithubIntegration(GITHUB_APP_ID, GITHUB_PRIVATE_KEY)
    access_token = integration.get_access_token(installation_id)
    return Github(access_token.token)


def get_pr_diff(repo: Repository, pr_number: int) -> str:
    """Fetch PR diff as a unified diff string."""
    pr = repo.get_pull(pr_number)
    # PyGithub doesn't directly expose diff, use raw request
    headers = {"Accept": "application/vnd.github.v3.diff"}
    import requests
    response = requests.get(pr.diff_url, headers=headers, timeout=30)
    response.raise_for_status()
    return response.text


def post_review(
    pr: PullRequest,
    summary: str,
    findings: list[dict],
) -> None:
    """Post an AI review with inline comments on the PR."""
    if not findings:
        pr.create_issue_comment(
            f"## AICodePR Review\n\n{summary}\n\nNo issues found."
        )
        return

    comments = []
    for f in findings:
        body = (
            f"**{f['severity'].upper()} · {f['title']}**\n\n"
            f"{f['description']}\n\n"
        )
        if f.get("suggestion"):
            body += f"```suggestion\n{f['suggestion']}\n```\n"

        comments.append({
            "path": f["file_path"],
            "line": f["line_number"],
            "side": "RIGHT",
            "body": body,
        })

    pr.create_review(
        body=f"## AICodePR Review\n\n{summary}",
        event="COMMENT",
        comments=comments,
    )
    logger.info(f"Posted review on PR #{pr.number}: {len(findings)} findings")
