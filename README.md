<!-- j1-brand:v2 -->
<div align="center">

# Hermes Voice

A self-hosted, AI-powered phone assistant — real-time voice conversations with an STT → LLM → TTS pipeline, built for FreeSWITCH, Asterisk, and 3CX.

[![GitHub](https://img.shields.io/badge/github-OneByJorah%2Fhermes--voice-FFB300?style=for-the-badge&labelColor=0d0d0c)](https://github.com/OneByJorah/hermes-voice)
[![License](https://img.shields.io/badge/license-MIT-FFB300?style=for-the-badge&labelColor=0d0d0c)](LICENSE)
[![Language](https://img.shields.io/badge/Python-FFB300?style=for-the-badge&labelColor=0d0d0c)](https://python.org)
[![Built by](https://img.shields.io/badge/built%20by-JorahOne%20LLC-FFB300?style=for-the-badge&labelColor=0d0d0c)](https://github.com/OneByJorah)

</div>

---

## Why This Exists

Phone trees and IVR menus are a terrible user experience. Hermes Voice replaces them with an AI-powered voice assistant that understands natural language. It plugs into existing PBX infrastructure (FreeSWITCH, Asterisk, 3CX), runs local STT via faster-whisper, routes through your LLM of choice, and responds with Piper TTS — all self-hosted, all private.

## Key Features

| Feature | Why It Matters |
|---|---|
| PBX integration (FreeSWITCH, Asterisk, 3CX) | Drops into existing phone infrastructure without replacing it |
| Local STT with faster-whisper | Speech-to-text runs on your GPU or CPU — no cloud dependency |
| Local TTS with Piper | Text-to-speech stays offline, low latency |
| Hybrid LLM support | Local (Ollama/llama.cpp) or hosted (Anthropic, OpenAI, OpenRouter) |
| Containerized deployment | `docker compose up` on any Linux host with Docker |

## Quick Start

```bash
git clone https://github.com/OneByJorah/hermes-voice.git
cd hermes-voice
cp .env.example .env   # configure PBX, LLM backend, etc.
docker compose up -d
```

Prerequisites: Docker + Docker Compose v2, a local Ollama instance (or other LLM backend), a Piper voice model, and optionally FreeSWITCH.

## Architecture

```
┌──────────┐     ┌──────────────┐     ┌──────────────┐
│  PBX      │────▶│  Hermes Voice│────▶│  STT / LLM   │
│  FreeSWITCH│    │  Brain        │     │  / TTS        │
│  Asterisk  │    │  (FastAPI)   │     │  faster-w     │
│  3CX       │    │               │     │  Piper        │
└──────────┘     └──────────────┘     └──────┬───────┘
                                              │
                                       ┌──────▼──────┐
                                       │  Ollama /    │
                                       │  OpenAI API   │
                                       └─────────────┘
```

## Documentation

| Doc | Description |
|---|---|
| [PBX Integration](docs/pbx.md) | Configuring FreeSWITCH, Asterisk, and 3CX |
| [Voice Models](docs/models.md) | Setting up STT and TTS models |
| [LLM Configuration](docs/llm.md) | Choosing between local and hosted LLMs |

---

## License

MIT © JorahOne, LLC — see [LICENSE](LICENSE)

<sub>Part of the JorahOne infrastructure ecosystem.</sub>
