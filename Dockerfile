FROM node:22-slim

# Install Python and system tools
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    curl \
    jq \
    && rm -rf /var/lib/apt/lists/*

# Pre-install Python dependencies so the skill works immediately
RUN pip3 install \
    youtube-transcript-api \
    google-generativeai \
    --break-system-packages \
    --no-cache-dir

# Install OpenClaw globally (Node 22 required)
RUN npm install -g openclaw@latest

# Create OpenClaw workspace directories
RUN mkdir -p /root/.openclaw/workspace/skills

# Copy OpenClaw config
COPY config/openclaw.json /root/.openclaw/openclaw.json

# Copy SOUL (agent personality)
COPY config/SOUL.md /root/.openclaw/workspace/SOUL.md

# Copy the youtube-summarizer skill
COPY skills/youtube-summarizer /root/.openclaw/workspace/skills/youtube-summarizer

# Make scripts executable
RUN chmod +x /root/.openclaw/workspace/skills/youtube-summarizer/scripts/*.py

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s \
    CMD openclaw status || exit 1

# Start the OpenClaw gateway
CMD ["openclaw", "gateway", "run"]
