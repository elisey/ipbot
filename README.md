# IP Bot

[![Release - Docker Build and Publish](https://github.com/elisey/ipbot/actions/workflows/ci-docker-publish.yml/badge.svg)](https://github.com/elisey/ipbot/actions/workflows/ci-docker-publish.yml)

A simple async Telegram bot that responds to `/ip` command with your public IP address.

## Features

- Async Telegram bot using python-telegram-bot
- Fetches public IP from ipify API
- Strategy pattern for extensible IP fetching methods
- Authorization based on Telegram user ID
- Dockerized deployment with docker-compose
- CI/CD pipeline to GitHub Container Registry
- Configuration via environment variables
- Comprehensive test coverage

## Requirements

- Python 3.13+
- UV package manager
- Docker and docker-compose (for deployment)
- Telegram bot token (from @BotFather)

## Quick Start

### Getting Your Telegram Credentials

#### 1. Create a Telegram Bot

1. Open Telegram and search for [@BotFather](https://t.me/BotFather)
2. Send `/newbot` command
3. Follow the prompts to choose a name and username for your bot
4. BotFather will give you a token that looks like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`
5. Save this token - you'll need it for configuration

#### 2. Get Your Telegram User ID

1. Open Telegram and search for [@userinfobot](https://t.me/userinfobot)
2. Send `/start` command
3. The bot will reply with your user ID (a number like `123456789`)
4. Save this ID - only this user will be able to use your IP bot

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

## Docker Deployment

### Option 1: Build Locally

```bash
# Build and start the container
docker compose up -d

# View logs
docker compose logs -f

# Stop the container
docker compose down
```

Make sure you have a `.env` file with your configuration before starting.

### Option 2: Use Pre-built Image from GHCR

Pull the latest image from GitHub Container Registry:

```bash
# Pull the image
docker pull ghcr.io/elisey/ipbot:latest

# Run with docker compose (using the pulled image)
docker compose up -d
```

The docker-compose configuration:
- Mounts your `.env` file as read-only
- Sets restart policy to `always`
- Runs as non-root user for security
- Uses UTC timezone

### Docker Management

```bash
# View running containers
docker ps

# View logs
docker compose logs -f ip-bot

# Restart the bot
docker compose restart

# Rebuild after code changes
docker compose up -d --build

# Stop and remove container
docker compose down
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

To add a new IP provider, simply:
1. Create a new class inheriting from `FetchStrategy`
2. Implement the `async def get_ip() -> str` method
3. Register it in the factory

## Troubleshooting

### Bot doesn't respond to commands

**Check authorization:**
- Verify `TELEGRAM_OWNER_ID` in `.env` matches your actual Telegram user ID
- Get your ID from @userinfobot to confirm

**Check bot token:**
- Verify `TELEGRAM_TOKEN` is correct (no extra spaces or quotes)
- Test the token is valid by visiting: `https://api.telegram.org/bot<YOUR_TOKEN>/getMe`

### "Unauthorized" message when sending /ip

- Your Telegram user ID doesn't match `TELEGRAM_OWNER_ID` in the configuration
- Only the specified owner can use the bot

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

# Docker deployment
docker compose logs -f ip-bot
```

### Docker container exits immediately

**Check configuration:**
```bash
# Verify .env file exists and has correct values
cat .env

# Check container logs
docker compose logs ip-bot
```

**Common issues:**
- Missing or invalid `.env` file
- Invalid bot token
- Network connectivity issues

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

### Using Released Images

Pull and run the latest release:

```bash
docker pull ghcr.io/elisey/ipbot:latest
docker compose up -d
```

Or use a specific version:

```bash
docker pull ghcr.io/elisey/ipbot:0.1.1
```

## License

MIT
