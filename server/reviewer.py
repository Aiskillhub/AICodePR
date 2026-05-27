import json
import logging
import re

import httpx

from server.config import (
    DEEPSEEK_API_KEY,
    DEEPSEEK_BASE_URL,
    CLAUDE_API_KEY,
    REVIEW_MODEL,
)
from server.prompt import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE
from server.schemas import ReviewResult

logger = logging.getLogger(__name__)


async def review_diff(diff_text: str) -> ReviewResult:
    """Run AI review on a diff and return structured results."""
    if REVIEW_MODEL == "claude" and CLAUDE_API_KEY:
        return await _review_with_claude(diff_text)
    return await _review_with_deepseek(diff_text)


async def _review_with_deepseek(diff_text: str) -> ReviewResult:
    """Use DeepSeek API for code review."""
    url = f"{DEEPSEEK_BASE_URL}/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": USER_PROMPT_TEMPLATE.format(diff_text)},
        ],
        "temperature": 0.1,
        "max_tokens": 2048,
    }

    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()

    content = data["choices"][0]["message"]["content"]
    return _parse_ai_response(content)


async def _review_with_claude(diff_text: str) -> ReviewResult:
    """Use Claude API for code review."""
    import anthropic

    client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)
    message = await client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        temperature=0.1,
        system=SYSTEM_PROMPT,
        messages=[
            {"role": "user", "content": USER_PROMPT_TEMPLATE.format(diff_text)},
        ],
    )

    content = message.content[0].text
    return _parse_ai_response(content)


def _parse_ai_response(content: str) -> ReviewResult:
    """Extract and validate JSON from AI response. Fail-closed: return empty on error."""
    # Try to extract JSON from possible markdown code blocks
    json_match = re.search(r"\{[\s\S]*\}", content)
    if not json_match:
        logger.warning("No JSON found in AI response")
        return ReviewResult(summary="AI review unavailable — could not parse response.")

    try:
        data = json.loads(json_match.group())
        return ReviewResult(**data)
    except (json.JSONDecodeError, Exception) as e:
        logger.warning(f"Failed to parse AI response: {e}\n{content[:500]}")
        return ReviewResult(summary="AI review unavailable — invalid response format.")
