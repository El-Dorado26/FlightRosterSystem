# Multi-stage Dockerfile for Flight Roster System backend
FROM python:3.12-slim as builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies for PostgreSQL and build tools
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        gcc \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy pyproject.toml first for dependency installation
COPY pyproject.toml /app/

RUN pip install --upgrade pip \
    && pip install --user --no-cache-dir -e .

# Stage 2: Runtime — lean final image
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install runtime dependencies for PostgreSQL
RUN apt-get update \
    && apt-get install -y --no-install-recommends libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copy only the virtual environment from builder
COPY --from=builder /root/.local /root/.local

# Copy application code
COPY . /app

# Add the user-site packages to PATH
ENV PATH=/root/.local/bin:$PATH

# Expose the port uvicorn will listen on
EXPOSE 8000

# Default command to run the FastAPI app with hot reload enabled
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
