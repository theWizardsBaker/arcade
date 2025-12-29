FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies for SSH connections
RUN apt-get update && apt-get install -y \
    openssh-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY arcade_downloader.py .
COPY interactive.py .
COPY config.example.json .

# Create directory for persistent data (queue, config)
RUN mkdir -p /data

# Set environment variable for queue file location
ENV QUEUE_FILE=/data/download_queue.json

# Make scripts executable
RUN chmod +x arcade_downloader.py interactive.py

# Set the entrypoint to Python
ENTRYPOINT ["python"]

# Default to showing help
CMD ["arcade_downloader.py", "--help"]
