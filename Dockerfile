FROM python:3.12-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app

# Set working directory
WORKDIR /app

# Install system build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code and static assets
COPY src/ ./src/
COPY static/ ./static/
COPY main.py .
COPY pyproject.toml .

# Create cache and output directories
RUN mkdir -p /app/.cache /app/outputs

# Expose FastAPI REST API port
EXPOSE 8000

# Default command launches FastAPI Uvicorn server
CMD ["python", "-m", "src.api.server"]
