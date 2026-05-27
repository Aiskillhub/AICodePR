# AICodePR

AI-powered code review for every pull request. Detects security vulnerabilities, logic errors, and performance issues before they merge.

## How it works

1. Install the GitHub App on your repos
2. Open a PR → AICodePR automatically reviews the diff
3. Inline comments appear directly on the PR with findings and fix suggestions

## What it catches

- SQL injection, XSS, command injection
- Hardcoded secrets and API keys
- N+1 queries and performance bottlenecks
- Logic errors and edge cases
- Unsafe external dependencies

## Powered by DeepSeek

High-quality reviews at minimal cost. ~¥0.001 per PR. Claude support included for advanced use cases.

## Quick start

1. Install [AICodePR](https://github.com/marketplace/aicodepr) from GitHub Marketplace
2. Grant access to your repositories
3. Open a PR — review appears automatically

## Self-host

See [SETUP.md](SETUP.md) for deployment guide.

## Pricing

| Plan | Price | |
|------|-------|---|
| Free | $0 | Up to 5 reviews/day |
| Pro | $12/mo | Unlimited reviews, 14-day trial |
| Team | $39/mo | Unlimited, priority queue, 14-day trial |

## License

MIT
