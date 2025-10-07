# -----------------------------
# IIUO Ads Dashboard Dockerfile
# Production-ready, multiple workers
# -----------------------------

# Use official Python slim image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for caching
COPY requirements.txt .

# Upgrade pip and install Python dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code and static assets
COPY app ./app
COPY templates ./templates
COPY static ./static

# Expose port for FastAPI
EXPOSE 8000

# Run the app with Uvicorn, 4 workers, production-ready
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
