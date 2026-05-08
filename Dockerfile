FROM python:3.12-slim

# System deps: ffmpeg for video, fonts for captions
RUN apt-get update && apt-get install -y \
    ffmpeg \
    fonts-liberation \
    fonts-dejavu-core \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create output directories
RUN mkdir -p output/videos output/images output/audio output/thumbnails \
             output/shorts assets/music data logs

# Default: run the pipeline once
CMD ["python", "main.py"]
