# Contributing to IP Bot

Thank you for your interest in contributing to IP Bot! This guide will help you set up your development environment and understand the project structure.

**Other Documentation:**
- [README](../README.md) - Quick start and basic usage for end-users
- [DEPLOYMENT](DEPLOYMENT.md) - Production deployment guide

## Development Requirements

- Python 3.14+
- UV package manager
- Git
- Docker and docker-compose (optional, for testing deployments)

## Development Setup

### 1. Install UV

Follow instructions at https://docs.astral.sh/uv/

Or use the quick install:

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 2. Clone and Install Dependencies

```bash
git clone https://github.com/elisey/ipbot.git
cd ipbot
uv sync
```

### 3. Configure the Bot

Create a `.env` file from the example:

```bash
cp .env.example .env
```

Edit `.env` and set your credentials:

```bash
TELEGRAM_TOKEN=your_bot_token_here
TELEGRAM_OWNER_ID=123456789
FETCHER_STRATEGY_ORDER=all
```

**Configuration Options:**

- `TELEGRAM_TOKEN` (required): Your bot token from @BotFather
- `TELEGRAM_OWNER_ID` (required): Your Telegram user ID - only this user can use the bot
- `FETCHER_STRATEGY_ORDER` (optional): IP fetchers to use, default: `all`

Available IP fetchers: `ipify`, `identme`, `ifconfig`, `ipinfo`, `custom`. The bot queries all configured fetchers in parallel for reliability.

**Using `all` keyword:** Set to `all` to automatically use all available fetchers. This is the default and recommended configuration.

### 4. Run the Bot Locally

```bash
# Using Taskfile (recommended)
task dev

# Or directly with uv
uv run python -m ipbot.main
```

The bot will start polling for messages. Send `/ip` to your bot in Telegram to test it.

## Development Workflow

This project uses [Task](https://taskfile.dev/) for development workflow automation. Available commands:

```bash
task dev          # Run the bot locally with uv
task test         # Run pytest with coverage
task lint         # Run ruff linter
task format       # Format code with ruff
task format-check # Check formatting without changes
task fix          # Fix formatting and auto-fixable lint issues
task check        # Run format-check, lint, and tests (pre-commit simulation)
```

### Running Tests

```bash
# Run all tests
task test

# Or directly with uv
uv run pytest

# Run specific test file
uv run pytest tests/test_bot.py

# Run with verbose output
uv run pytest -v
```

All tests use async/await patterns and mock external dependencies (Telegram API, HTTP requests).

### Code Quality

Pre-commit hooks are configured to run automatically on git commit:

- Ruff linter checks
- Ruff formatter checks
- Unit tests (pytest)

To manually run pre-commit checks:

```bash
task check
```

### Dependency Management

This project uses [Renovate](https://docs.renovatebot.com/) for automated dependency updates:

- **Automatic updates**: Renovate checks for updates weekly (every Monday)
- **Grouped PRs**: Non-major updates are grouped into a single PR to reduce noise
- **Separate PRs**: Major version updates get individual PRs for careful review
- **Monitors**: Python packages, GitHub Actions, pre-commit hooks, and Docker base images
- **Manual merge**: All PRs require manual review and merge after pre-commit hooks pass

Renovate PRs will automatically trigger pre-commit hooks (ruff formatting and pytest), ensuring all dependency updates are validated before merge.

## Project Structure

```
ipbot/
├── .github/
│   └── workflows/
│       └── ci-docker-publish.yml  # CI/CD pipeline
├── docker/
│   └── Dockerfile                 # Multi-stage Docker build
├── src/ipbot/
│   ├── __init__.py
│   ├── main.py                    # Application entry point
│   ├── bot.py                     # Telegram command handlers
│   ├── config.py                  # Configuration with Pydantic Settings
│   ├── logger.py                  # Logging setup
│   ├── factory.py                 # IP fetcher factory (strategy pattern)
│   ├── orchestrator.py            # Parallel fetch orchestrator
│   ├── formatter.py               # Result formatter
│   ├── result.py                  # Result data models
│   └── fetchers/
│       ├── __init__.py
│       ├── base.py                # FetchStrategy ABC
│       ├── exceptions.py          # Custom exceptions
│       ├── http_fetcher.py        # Common HTTP helper
│       ├── ipify.py               # Ipify strategy implementation
│       ├── custom.py              # Custom strategy implementation
│       ├── identme.py             # Ident.me strategy implementation
│       ├── ifconfig.py            # Ifconfig.me strategy implementation
│       └── ipinfo.py              # Ipinfo.io strategy implementation
├── tests/                         # Unit tests with pytest
├── docker-compose.yml             # Docker deployment config
├── pyproject.toml                 # Project dependencies (UV)
├── Taskfile.yaml                  # Development tasks
├── .env.example                   # Example environment variables
└── README.md
```

## Architecture

The bot uses the **Strategy Pattern** with **Parallel Orchestration** for resilient IP fetching:

### Key Components

- **`FetchStrategy` (ABC)**: Defines the interface for IP fetching strategies with two methods:
  - `async def get_ip() -> str`: Fetches the IP address
  - `def get_name() -> str`: Returns the display name of the fetcher

- **Fetcher Implementations**:
  - `IpifyStrategy`: Fetches from ipify.org (JSON API)
  - `IdentMeStrategy`: Fetches from ident.me (plain text)
  - `IfconfigStrategy`: Fetches from ifconfig.me (plain text)
  - `IpinfoStrategy`: Fetches from ipinfo.io (plain text)
  - `CustomStrategy`: Fetches from ipinfo.io (plain text)

- **`ParallelFetchOrchestrator`**: Runs all configured fetchers in parallel using `asyncio.gather()`, collects results, and determines consensus

- **`ResultFormatter`**: Formats fetcher results into user-friendly messages with status indicators (🟢/🟡/❌)

- **`HttpFetcher`**: Common HTTP client helper with timeout handling and error categorization

### How Parallel Fetching Works

1. **Initialization** (`main.py`): Creates all fetchers based on config and wraps them in the orchestrator
2. **Execution** (`bot.py`): When user requests `/ip`, orchestrator runs all fetchers concurrently
3. **Consensus** (`orchestrator.py`): Compares successful results - all must match for consensus
4. **Formatting** (`formatter.py`): Displays results with appropriate emoji indicators based on status

### Adding a New IP Provider

To add a new IP provider:

1. Create a new class inheriting from `FetchStrategy` in `src/ipbot/fetchers/`
2. Implement both required methods:
   - `async def get_ip() -> str` - Fetch and return the IP address
   - `def get_name() -> str` - Return a display name (e.g., "myservice.com")
3. Use `HttpFetcher` helper for HTTP requests (handles timeouts and errors)
4. Register it in the factory (`src/ipbot/factory.py`) in the `STRATEGIES` dictionary
5. Add comprehensive tests in `tests/test_fetchers.py`
6. Update documentation

Example:

```python
from ipbot.fetchers.base import FetchStrategy
from ipbot.fetchers.http_fetcher import HttpFetcher

class MyProviderStrategy(FetchStrategy):
    MY_URL = "https://api.myprovider.com/ip"
    TIMEOUT = 3.0

    async def get_ip(self) -> str:
        """Fetch IP from my provider."""
        http_fetcher = HttpFetcher(timeout=self.TIMEOUT)
        response = await http_fetcher.fetch(self.MY_URL, "myprovider")
        return response.text.strip()

    def get_name(self) -> str:
        """Return display name."""
        return "myprovider.com"
```

Then register in `factory.py`:
```python
STRATEGIES = {
    "myprovider": MyProviderStrategy,
    # ... existing strategies
}
```

**Automatic inclusion with `all` keyword:** Once registered, your new fetcher will automatically be included when users set `FETCHER_STRATEGY_ORDER=all` (the default), providing seamless integration.

## Development Troubleshooting

### Pre-commit hooks fail

```bash
# Fix formatting and auto-fixable issues
task fix

# Check what's wrong
task check

# Manually run hooks
pre-commit run --all-files
```

### Tests fail

```bash
# Run tests with verbose output
uv run pytest -v

# Run specific test
uv run pytest tests/test_bot.py -v

# Check for missing dependencies
uv sync
```

### Bot doesn't respond to commands

**Check authorization:**
- Verify `TELEGRAM_OWNER_ID` in `.env` matches your actual Telegram user ID
- Get your ID from @userinfobot to confirm

**Check bot token:**
- Verify `TELEGRAM_TOKEN` is correct (no extra spaces or quotes)
- Test the token is valid by visiting: `https://api.telegram.org/bot<YOUR_TOKEN>/getMe`

### Bot starts but doesn't fetch IP

**Check network connectivity:**
```bash
# Test if you can reach ipify API
curl https://api.ipify.org?format=json
```

**Check bot logs:**
```bash
# Local development
task dev  # Look for error messages
```

## Release Process

This project uses automated releases via GitHub Actions. When you push a version tag, the workflow automatically builds and publishes Docker images to GitHub Container Registry.

### Creating a New Release

1. **Ensure all changes are committed and pushed to main:**
   ```bash
   git status
   git push
   ```

2. **Create and push a version tag:**
   ```bash
   # Create a tag (use semantic versioning: v0.1.0, v1.2.3, etc.)
   git tag v0.1.1

   # Push the tag to trigger the release workflow
   git push origin v0.1.1
   ```

3. **Monitor the workflow:**
   - Visit: `https://github.com/elisey/ipbot/actions`
   - The "Release - Docker Build and Publish" workflow will automatically:
     - Build the Docker image
     - Push to GitHub Container Registry with two tags:
       - Semantic version (e.g., `0.1.1`)
       - `latest`

4. **Published images will be available at:**
   ```
   ghcr.io/elisey/ipbot:0.1.1
   ghcr.io/elisey/ipbot:latest
   ```

## Testing Your Changes with Docker

Before creating a PR, test your changes in a Docker environment:

```bash
# Build and start the container
docker compose up -d

# View logs
docker compose logs -f

# Stop the container
docker compose down
```

## Contributing Guidelines

1. **Fork the repository** and create your feature branch from `main`
2. **Write tests** for any new functionality
3. **Follow the code style** - run `task check` before committing
4. **Write clear commit messages** describing what and why
5. **Update documentation** if you change functionality
6. **Ensure all tests pass** before submitting a PR

## Getting Help

- Check existing [Issues](https://github.com/elisey/ipbot/issues)
- Create a new issue if you find a bug or have a feature request
- For deployment help, see [DEPLOYMENT.md](DEPLOYMENT.md)
- For usage help, see [README.md](../README.md)

## License

MIT
