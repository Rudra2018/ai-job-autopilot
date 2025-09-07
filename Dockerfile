# 🤖 AI Job Autopilot - Docker Configuration
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    xvfb \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libdrm2 \
    libxkbcommon0 \
    libxss1 \
    libgconf-2-4 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers
RUN playwright install --with-deps chromium

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p config dashboard data screenshots logs ml_models

# Download AI model during build
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('TechWolf/JobBERT-v3').save('ml_models/jobbert_v3')"

# Set permissions
RUN chmod +x *.py

# Expose Streamlit port
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Default command (can be overridden)
CMD ["python", "-m", "streamlit", "run", "ui/dashboard_ui.py", "--server.port=8501", "--server.address=0.0.0.0"]
