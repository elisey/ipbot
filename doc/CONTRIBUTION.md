# Contributing to IP Bot

Thank you for your interest in contributing to IP Bot! This guide will help you set up your development environment and understand the project structure.

**Other Documentation:**
- [README](../README.md) - Quick start and basic usage for end-users
- [DEPLOYMENT](DEPLOYMENT.md) - Production deployment guide

## Development Requirements

- Python 3.13+
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
FETCHER_STRATEGY_ORDER=ipify
SERVER_REPLY_FORMAT=🌐 Your public IP is: {ip}
```

**Configuration Options:**

- `TELEGRAM_TOKEN` (required): Your bot token from @BotFather
- `TELEGRAM_OWNER_ID` (required): Your Telegram user ID - only this user can use the bot
- `FETCHER_STRATEGY_ORDER` (optional): IP fetching strategy, default: `ipify`
- `SERVER_REPLY_FORMAT` (optional): Message format, default: `🌐 Your public IP is: {ip}`

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

To manually run pre-commit checks:

```bash
task check
```

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
│   └── fetchers/
│       ├── __init__.py
│       ├── base.py                # FetchStrategy ABC
│       └── ipify.py               # Ipify strategy implementation
├── tests/                         # Unit tests with pytest
├── docker-compose.yml             # Docker deployment config
├── pyproject.toml                 # Project dependencies (UV)
├── Taskfile.yaml                  # Development tasks
├── .env.example                   # Example environment variables
└── README.md
```

## Architecture

The bot uses the **Strategy Pattern** for IP fetching, making it easy to add new IP providers:

- `FetchStrategy` (ABC): Defines the interface for IP fetching strategies
- `IpifyStrategy`: Implements fetching from api.ipify.org
- `IPFetcherFactory`: Creates the appropriate fetcher based on configuration

### Adding a New IP Provider

To add a new IP provider:

1. Create a new class inheriting from `FetchStrategy` in `src/ipbot/fetchers/`
2. Implement the `async def get_ip() -> str` method
3. Register it in the factory (`src/ipbot/factory.py`)
4. Add tests for your new strategy
5. Update documentation

Example:

```python
from ipbot.fetchers.base import FetchStrategy

class MyProviderStrategy(FetchStrategy):
    async def get_ip(self) -> str:
        # Your implementation here
        pass
```

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
