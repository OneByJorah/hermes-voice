# VoiceCortex (Hermes Voice)

Self-hosted phone AI assistant — real-time AI voice conversations over telephone via STT > LLM > TTS pipeline.

![status](https://img.shields.io/badge/status-active-FFB300?style=flat-square)
![language](https://img.shields.io/badge/python-3.11+-0d0d0c?style=flat-square)
![license](https://img.shields.io/badge/license-MIT-FFB300?style=flat-square)

## Overview

VoiceCortex (branded "Hermes Voice") is a self-hosted AI phone assistant that enables real-time voice conversations over telephone lines. Audio from a phone call is streamed through a pipeline: Voice Activity Detection > Speech-to-Text (faster-whisper) > LLM inference (Ollama/llama.cpp) > Text-to-Speech (Piper), then played back to the caller. Works with FreeSWITCH, Asterisk/FreePBX, and 3CX. All processing can run locally — no cloud dependencies required.

## Features

- Phone integration — FreeSWITCH WebSocket, Asterisk ARI, and 3CX compatible
- Real-time pipeline — VAD > STT > LLM > TTS with sub-second latency
- Local AI stack — faster-whisper (STT), Ollama/llama.cpp (LLM), Piper (TTS)
- Docker Compose deployment — one command to start
- Transport-agnostic core — same brain works with any PBX
- GPU accelerated — CUDA support for STT and optional LLM inference
- Hybrid mode — local STT/TTS with hosted LLM API (OpenAI, Anthropic, OpenRouter)

## Architecture / Tech Stack

- **STT**: faster-whisper (local, GPU-optional)
- **LLM**: Ollama / llama.cpp (local) or hosted API
- **TTS**: Piper (local, fast neural TTS)
- **PBX**: FreeSWITCH, Asterisk/FreePBX, 3CX
- **Transport**: WebSocket (FreeSWITCH), ARI (Asterisk)
- **Deployment**: Docker Compose

## Installation

```bash
git clone https://github.com/OneByJorah/VoiceCortex.git
cd VoiceCortex

cp .env.example .env  # Configure PBX connection, LLM endpoint
docker compose up -d
```

## Configuration

| Variable | Description |
|----------|-------------|
| `OLLAMA_URL` | Ollama endpoint (default: `http://localhost:11434`) |
| `LLM_MODEL` | Model to use (default: `llama3`) |
| `STT_MODEL` | Whisper model size (default: `base`) |
| `TTS_VOICE` | Piper voice (default: `en_US-lessac-medium`) |
| `FREESWITCH_URL` | FreeSWITCH WebSocket URL |

See `.env.example` for full options.

## License

MIT — see [LICENSE](LICENSE).

---
Part of the JorahOne / J1 ecosystem — voice AI for self-hosted telephony.
