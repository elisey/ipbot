# Multi-stage build for optimized image size
FROM python:3.13-slim AS builder

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set working directory
WORKDIR /app

# Copy dependency files
COPY ../pyproject.toml ../uv.lock ./

# Sync dependencies (no dev dependencies)
RUN uv sync --frozen --no-dev

# Runtime stage
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Copy application source code
COPY ../src/ipbot ./ipbot

# Create non-root user
RUN useradd -m -u 1000 ipbot && \
    chown -R ipbot:ipbot /app

# Switch to non-root user
USER ipbot

# Add virtual environment to PATH
ENV PATH="/app/.venv/bin:$PATH"

# Run the application
CMD ["python", "-m", "ipbot.main"]
