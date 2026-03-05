# Contributing Guide

## Development Setup

1. Create and activate a virtual environment.
2. Install dependencies.
3. Run lint and tests before opening a PR.

```powershell
python -m venv .venv
.\.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install ruff
pytest
```

## Pull Request Rules

- Keep PRs focused and small.
- Add tests for behavior changes.
- Update docs if API, CLI, or architecture changes.
- Ensure CI passes before requesting review.

## Code Style

- Follow `ruff` checks.
- Prefer small, pure functions.
- Keep user-facing messages clear and concise.
