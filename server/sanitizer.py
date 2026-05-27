import re

# Patterns for secrets that should be redacted before sending to AI API
SECRET_PATTERNS = [
    (r"(?i)(api[_-]?key|apikey|api[_-]?secret|secret[_-]?key)\s*[:=]\s*[\"'`]?[^\"'`\s]{8,}[\"'`]?", '[REDACTED]'),
    (r"(?i)(password|passwd|pwd)\s*[:=]\s*[\"'`]?[^\"'`\s]+[\"'`]?", '[REDACTED]'),
    (r"(?i)(token|auth[_-]?token|access[_-]?token)\s*[:=]\s*[\"'`]?[^\"'`\s]{8,}[\"'`]?", '[REDACTED]'),
    (r"-----BEGIN (RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----[\s\S]*?-----END \1?PRIVATE KEY-----", '[REDACTED PRIVATE KEY]'),
    (r"(?i)(ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9_]{36,}", '[REDACTED GITHUB TOKEN]'),
    (r"sk-[A-Za-z0-9]{32,}", '[REDACTED API KEY]'),
    (r"(?i)Bearer\s+[A-Za-z0-9_\-\.]{20,}", '[REDACTED BEARER TOKEN]'),
    (r"(?i)jdbc:[a-z]+://[^/\s]+/[^\s]+\?user=[^\s&]+&password=[^\s&]+", '[REDACTED JDBC URL]'),
]

IGNORED_FILE_PATTERNS = [
    r"(^|/)package-lock\.json$",
    r"(^|/)yarn\.lock$",
    r"(^|/)pnpm-lock\.yaml$",
    r"(^|/)Cargo\.lock$",
    r"(^|/)Gemfile\.lock$",
    r"(^|/)poetry\.lock$",
    r"(^|/)Pipfile\.lock$",
    r"(^|/)composer\.lock$",
    r"(^|/)\.lock$",
    r"\.min\.(js|css)$",
    r"\.(png|jpg|jpeg|gif|ico|svg|webp|woff2?|ttf|eot)$",
    r"(^|/)\.git/",
]


def sanitize_diff(diff_text: str) -> str:
    """Remove secrets from diff text before sending to AI."""
    for pattern, replacement in SECRET_PATTERNS:
        diff_text = re.sub(pattern, replacement, diff_text)
    return diff_text


def should_ignore_file(file_path: str) -> bool:
    """Check if a file should be skipped in review."""
    for pattern in IGNORED_FILE_PATTERNS:
        if re.search(pattern, file_path):
            return True
    return False


def split_diff_by_file(diff_text: str, max_chars: int) -> list[str]:
    """Split a large diff into per-file chunks, respecting max_chars.
    Files that can't fit in max_chars are truncated individually.
    Returns a list of diff chunks, each under max_chars.
    """
    if not diff_text.strip():
        return []

    files = diff_text.split("\ndiff --git ")
    if not files:
        return []

    chunks: list[str] = []
    current_chunk = ""

    for i, file_diff in enumerate(files):
        if i > 0:
            file_diff = "diff --git " + file_diff

        if len(file_diff) > max_chars:
            if current_chunk:
                chunks.append(current_chunk)
                current_chunk = ""
            # Split oversized file into smaller pieces
            for start in range(0, len(file_diff), max_chars):
                chunks.append(file_diff[start:start + max_chars] + "\n... (truncated)")
            continue

        if len(current_chunk) + len(file_diff) > max_chars:
            chunks.append(current_chunk)
            current_chunk = file_diff
        else:
            current_chunk += file_diff

    if current_chunk:
        chunks.append(current_chunk)

    return chunks if chunks else [diff_text[:max_chars]]
