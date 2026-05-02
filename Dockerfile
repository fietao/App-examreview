# Java Study App - Docker Container
# Build: docker build -t java-study-app .
# Run:   docker run -p 5000:5000 java-study-app

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy application files
COPY requirements.txt .
COPY study_app.py .
COPY questions.json .
COPY .env.example .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Ollama (needs to connect to existing Ollama server)
# The app will try to connect to OLLAMA_BASE_URL
ENV OLLAMA_BASE_URL=http://host.docker.internal:11434

# Set default environment variables
ENV SERVER_HOST=0.0.0.0
ENV SERVER_PORT=5000
ENV OLLAMA_MODEL=qwen2.5:14b
ENV AUTO_OPEN_BROWSER=false

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000').read()" || exit 1

# Run the app
CMD ["python", "study_app.py"]
