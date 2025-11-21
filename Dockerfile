## Multi-stage Dockerfile optimized for smaller runtime image

### Builder stage
FROM python:3.11-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install build dependencies for wheels where needed
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential \
       gcc \
       gfortran \
       libatlas-base-dev \
       ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./

# Upgrade pip and install packages into a separate target directory
RUN python3 -m pip install --upgrade pip wheel setuptools \
    && python3 -m pip install --upgrade --target=/install -r requirements.txt

COPY . /app


### Final runtime stage
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Minimal runtime packages
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy installed python packages from the builder stage
COPY --from=builder /install /usr/local/lib/python3.11/site-packages

# Copy application files
COPY --from=builder /app /app

# Create a non-root user and set permissions
RUN useradd -m appuser || true
RUN chown -R appuser:appuser /app
USER appuser

EXPOSE 8501

CMD ["streamlit", "run", "streamlit_app.py", "--server.port", "8501", "--server.headless", "true", "--server.enableCORS", "false"]
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install system packages required for some numeric packages
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential \
       gcc \
       gfortran \
       libatlas-base-dev \
       ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python deps
COPY requirements.txt ./
RUN python3 -m pip install --upgrade pip \
    && python3 -m pip install -r requirements.txt

# Copy app files
COPY . /app

# Create a non-root user and set permissions
RUN useradd -m appuser || true
RUN chown -R appuser:appuser /app
USER appuser

EXPOSE 8501

ENV STREAMLIT_SERVER_PORT=8501

CMD ["streamlit", "run", "streamlit_app.py", "--server.port", "8501", "--server.headless", "true", "--server.enableCORS", "false"]
