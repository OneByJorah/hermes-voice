# =============================================================================
# Hermes Voice — Self-hosted voice assistant call stack
# JorahOne
#
# STT (faster-whisper) -> LLM (Ollama/llama.cpp/API) -> TTS (Piper)
# =============================================================================
FROM python:3.11-slim AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg libsndfile1 git build-essential curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY bot/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ---------------------------------------------------------------------------
FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg libsndfile1 curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

COPY bot/ /app/bot/
COPY .env.example /app/.env.example

# Default persona file
COPY bot/persona.txt /app/persona.txt

EXPOSE 8765

HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD python3 -c "import socket; s=socket.socket(); s.settimeout(5); s.connect(('localhost', ${BOT_WS_PORT:-8765})); s.close()" || exit 1

CMD ["python3", "bot/server.py"]
