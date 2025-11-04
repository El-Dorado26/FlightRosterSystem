# Multi-stage Dockerfile for Flight Roster System backend (FastAPI)
# Stage 1: Builder — install dependencies
FROM python:3.12-slim as builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install build dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy source and install dependencies into a virtual env
COPY ./backend /app
RUN pip install --upgrade pip
RUN pip install --user --no-cache-dir fastapi uvicorn

# Stage 2: Runtime — lean final image
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Copy only the virtual environment from builder
COPY --from=builder /root/.local /root/.local

# Copy application code
COPY --from=builder /app /app

# Add the user-site packages to PATH
ENV PATH=/root/.local/bin:$PATH

# Expose the port uvicorn will listen on
EXPOSE 8000

# Default command to run the FastAPI app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
