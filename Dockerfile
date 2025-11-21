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
