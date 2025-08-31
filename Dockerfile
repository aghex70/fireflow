# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src \
    FLASK_APP=src/app.py \
    FLASK_ENV=production \
    ENVIRONMENT=production

# Security note: Secrets should be provided via Docker secrets or environment variables at runtime
# NEVER include secrets in the Docker image!

# Install system dependencies and uv
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        libc6-dev \
        curl \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir uv

# Copy project files for dependency resolution
COPY pyproject.toml uv.lock* README.md ./

# Install Python dependencies using uv
RUN uv sync --frozen --no-dev

# Copy application code
COPY src/ ./src/
COPY alembic.ini ./
COPY alembic/ ./alembic/

# Create data directory for SQLite database
RUN mkdir -p /app/data

# Create convenient aliases for common commands
RUN echo 'alias alembic="uv run alembic"' >> /root/.bashrc && \
    echo 'alias python="uv run python"' >> /root/.bashrc && \
    echo 'alias pytest="uv run pytest"' >> /root/.bashrc

# Expose port
EXPOSE 12345

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD uv run python -c "import requests; requests.get('http://localhost:12345/health', timeout=5)"

# Run the application using uv
CMD ["uv", "run", "python", "src/app.py"]

