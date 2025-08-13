# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

TikTok Uploader is a Selenium-based automated video uploader for TikTok. It uses browser automation to upload videos with descriptions, schedules, product links, and other features by simulating user interactions with the TikTok website.

## Key Architecture

### Core Components

- **Upload Module** (`src/tiktok_uploader/upload.py`): Main upload logic handling single and batch video uploads to TikTok
- **Auth Backend** (`src/tiktok_uploader/auth.py`): Handles authentication via cookies, sessionid, or username/password
- **Browser Management** (`src/tiktok_uploader/browsers.py`): Manages Selenium WebDriver instances for Chrome, Firefox, Safari, Edge with anti-detection measures
- **CLI Interface** (`src/tiktok_uploader/cli.py`): Command-line interface for the uploader and authentication tools
- **Proxy Extension** (`src/tiktok_uploader/proxy_auth_extension/`): Chrome extension for authenticated proxy support

### Authentication Flow

The uploader uses browser cookies to authenticate with TikTok, bypassing the need for direct API access. Authentication priority:
1. Cookies from file (NetScape format)
2. Cookie list (Selenium-compatible dictionaries)
3. SessionID
4. Username/Password (fallback, creates cookies)

## Development Commands

### Running the Application

```bash
# Run CLI directly with uv
uv run tiktok-uploader -v video.mp4 -d "description" -c cookies.txt

# Run as Python module
uv run python -m tiktok_uploader
```

### Testing

```bash
# Run all tests
uv run pytest

# Run all tests with verbose output
uv run pytest -v

# Run specific test file
uv run pytest tests/test_upload.py

# Run with specific test selection (by name pattern)
uv run pytest -k "test_name"

# Run specific test function
uv run pytest tests/test_upload.py::test_function_name

# Run tests for specific feature
uv run pytest -k "visibility"

# Run tests with coverage report
uv run pytest --cov=src/tiktok_uploader

# Run tests and stop on first failure
uv run pytest -x
```

### Code Quality

```bash
# Lint code with ruff (check for errors)
uv run ruff check .

# Format code with ruff (apply consistent formatting)
uv run ruff format .

# Check formatting without applying changes
uv run ruff format --check .

# Type checking with mypy
uv run mypy src/tiktok_uploader/

# Combined quality check workflow (run all before committing)
uv run ruff check . && uv run ruff format . && uv run mypy src/tiktok_uploader/

# Complete CI workflow (matches GitHub Actions - REQUIRED before committing)
uv run ruff check . && uv run ruff format --check . && uv run mypy . && uv run pytest
```

### Package Management

```bash
# Install all dependencies including dev
uv sync --all-groups

# Add new dependency
uv add package_name

# Add dev dependency
uv add --group dev package_name
```

## Development Workflow

### Before Committing Changes

**ALWAYS run the complete quality check workflow:**

```bash
# 1. Run tests to ensure functionality
uv run pytest

# 2. Check for linting errors
uv run ruff check .

# 3. Format code consistently
uv run ruff format .

# 4. Verify type checking
uv run mypy src/tiktok_uploader/

# Complete CI workflow - REQUIRED before committing (matches GitHub Actions)
uv run ruff check . && uv run ruff format --check . && uv run mypy . && uv run pytest
```

### Git Workflow

```bash
# Create feature branch
git checkout -b feature-name

# Make changes and test them
# ... code changes ...

# Run complete CI workflow (REQUIRED before committing)
uv run ruff check . && uv run ruff format --check . && uv run mypy . && uv run pytest

# Stage and commit changes
git add .
git commit -m "feat: descriptive commit message"

# Push to remote
git push -u origin feature-name
```

### Testing New Features

When adding new features:
1. **Write tests first** - Add test cases in `tests/` directory
2. **Test locally** - Use provided test videos and session credentials
3. **Verify with screenshots** - For UI interactions, capture browser screenshots
4. **Run full test suite** - Ensure no regressions

## Important Implementation Details

### Video Upload Process

1. Browser initialization with anti-detection measures
2. Authentication via cookies injection
3. Navigation to TikTok upload page
4. File selection and metadata input
5. Optional: schedule configuration, product linking
6. Submit and verification

### Anti-Detection Measures

- Custom Chrome options to avoid Selenium detection
- User-agent spoofing
- Webdriver property removal
- Stealth JavaScript injection

### Error Handling

- Automatic retry logic for transient failures
- Detailed logging via Python logging module
- Failed video tracking in batch uploads
- Timeout configurations in `config.toml`

## Configuration

Main configuration file: `src/tiktok_uploader/config.toml`
- Contains timeouts, URLs, and XPath selectors
- Explicit wait times for Selenium operations
- TikTok page element locators

## Testing Approach

- Unit tests for browser initialization and upload logic
- Mock-based testing to avoid actual TikTok uploads
- Test files in `tests/` directory
- Uses pytest with freezegun for time-based testing