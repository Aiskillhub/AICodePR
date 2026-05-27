import os
from dotenv import load_dotenv

load_dotenv()

GITHUB_APP_ID = os.getenv("GITHUB_APP_ID", "")
GITHUB_WEBHOOK_SECRET = os.getenv("GITHUB_WEBHOOK_SECRET", "")

# Load private key from file if available, otherwise from env
_GITHUB_PRIVATE_KEY_FILE = os.getenv(
    "GITHUB_PRIVATE_KEY_FILE",
    os.path.join(os.path.dirname(__file__), "github-app-key.pem"),
)
if os.path.exists(_GITHUB_PRIVATE_KEY_FILE):
    with open(_GITHUB_PRIVATE_KEY_FILE) as f:
        GITHUB_PRIVATE_KEY = f.read()
else:
    GITHUB_PRIVATE_KEY = os.getenv("GITHUB_PRIVATE_KEY", "")

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY", "")

REVIEW_MODEL = os.getenv("REVIEW_MODEL", "deepseek")
MAX_DIFF_CHARS = int(os.getenv("MAX_DIFF_CHARS", "8000"))
