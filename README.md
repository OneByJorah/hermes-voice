# Hermes Voice — Self-Hosted Phone AI Assistant

**Version:** v1.0  
**Status:** Active Development  
**Repository:** https://github.com/OneByJorah/hermes-voice

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Technology Stack](#technology-stack)
- [Features](#features)
- [Getting Started](#getting-started)
- [Environment Variables](#environment-variables)
- [LLM Backends](#llm-backends)
- [PBX Integration](#pbx-integration)
- [Service Management](#service-management)
- [Security](#security)
- [Performance](#performance)
- [Troubleshooting](#troubleshooting)
- [Known Limitations](#known-limitations)
- [Roadmap](#roadmap)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)
- [Author](#author)

---

## Overview

Hermes Voice lets you talk to a self-hosted Hermes agent over a real phone call. It bridges telephony (FreeSWITCH or Asterisk/ARI) with a local LLM brain (Ollama, llama.cpp, or a hosted API) using faster-whisper for STT and Piper for TTS.

Bring your own PBX (3CX, FreePBX, Asterisk, or the bundled FreeSWITCH) and your own LLM backend. The bot logic is transport-agnostic — `hermes_brain.py` owns the audio pipeline, while `server.py` and `server_asterisk.py` own the PBX-specific transport.

---

## Architecture

```
Caller Phone
    │
    ▼
PBX Layer (pick one)
├── FreeSWITCH (bundled, default) ── mod_audio_fork ──┐
├── Asterisk / FreePBX ── ARI + externalMedia ───────┤
├── 3CX trunk ─────────────────────────────────────────┘
│
▼
hermes_brain.py
├── STT: faster-whisper (GPU or CPU)
├── LLM: Ollama / llama.cpp / OpenAI-compatible API
├── TTS: Piper ONNX runtime
└── Session: per-call (non-persistent today)
```

**Core loop per call:**
`audio in → VAD → STT → LLM → TTS → audio out`

---

## Technology Stack

| Layer | Stack |
|---|---|
| Telephony | FreeSWITCH, Asterisk/ARI, 3CX trunk |
| Bot runtime | Python |
| STT | faster-whisper |
| TTS | Piper (ONNX) |
| LLM | Ollama, llama.cpp, or OpenAI-compatible API |
| Transport | WebSocket (FreeSWITCH), ARI HTTP (Asterisk) |
| Orchestration | Docker Compose |
| VCS | Git + GitHub (`github.com/OneByJorah/hermes-voice`) |

---

## Features

- **Multiple PBX transports**: FreeSWITCH (default), Asterisk/ARI, FreePBX, 3CX trunking
- **Local-first voice stack**: faster-whisper STT + Piper TTS offline capable
- **Flexible LLM backends**: Ollama, llama.cpp, or hosted API — switchable via `.env` only
- **Shared brain core**: `hermes_brain.py` is reused across transports
- **Docker-native**: one-compose bootstrap for FreeSWITCH path
- **Typical call flow**: answer → listen → transcribe → think → speak → hangup

---

## Getting Started

```bash
# 1. Clone
git clone https://github.com/OneByJorah/hermes-voice.git
cd hermes-voice

# 2. Environment
cp .env.example .env
# Edit .env for your LLM backend and PBX choice.

# 3. Piper voices
mkdir -p piper-voices && cd piper-voices
curl -LO https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/amy/medium/en_US-amy-medium.onnx
curl -LO https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/amy/medium/en_US-amy-medium.onnx.json
cd ..

# 4. Start FreeSWITCH path (default)
docker compose --profile freeswitch up -d --build

# 5. Register a softphone against FreeSWITCH and dial 8500
```

---

## Environment Variables

Configure in `.env`. Only the vars for your chosen `LLM_BACKEND` and PBX need values.

| Variable | Purpose |
|---|---|
| `LLM_BACKEND` | `ollama` (default), `llamacpp`, or `api` |
| `OLLAMA_HOST`, `OLLAMA_MODEL` | Ollama server URL + model |
| `LLAMACPP_HOST` | llama-server OpenAI-compat endpoint |
| `API_PROVIDER` | `anthropic` or `openai` |
| `API_BASE_URL`, `API_MODEL`, `API_KEY` | Hosted API settings |
| `WHISPER_MODEL` | `base.en`, `small.en`, or `medium.en` |
| `WHISPER_DEVICE` | `cuda` or `cpu` |
| `PIPER_VOICE` | Path to Piper ONNX voice model |
| `BOT_WS_PORT` | Bot WebSocket port (default `8765`) |
| `SAMPLE_RATE` | Audio sample rate; match your codec |

---

## LLM Backends

| Backend | When to use | Key vars |
|---|---|---|
| `ollama` | Local model on your GPU box (default) | `OLLAMA_HOST`, `OLLAMA_MODEL` |
| `llamacpp` | Dedicated `llama-server` with GGUF | `LLAMACPP_HOST` |
| `api` | Hosted Anthropic or OpenAI-compatible | `API_PROVIDER`, `API_BASE_URL`, `API_MODEL`, `API_KEY` |

All three use the same `ask_llm()` in `bot/hermes_brain.py`. Switching is an env change only.

`llamacpp` expects an OpenAI-compatible `/v1/chat/completions` endpoint running locally.
`api` with `API_PROVIDER=openai` works for OpenAI, OpenRouter, or any compatible gateway.

---

## PBX Integration

### FreeSWITCH (default)
`docker compose --profile freeswitch up -d --build`
Dial extension `8500`.

### 3CX
Create a SIP trunk in 3CX pointing at the FreeSWITCH box on `IP:5060`, then route a DID or extension to dial out to `8500`.

### FreePBX
Either trunk into the bundled FreeSWITCH (same as 3CX), or use FreePBX’s own Asterisk with `server_asterisk.py`.

### Asterisk / ARI — `server_asterisk.py`
Uses Asterisk **ARI + externalMedia**:
1. Enable ARI (`ari.conf`) and `http.conf`.
2. Add a dialplan extension that runs `Stasis(hermes-voice)`.
3. Run `python bot/server_asterisk.py` with `ARI_HOST`, `ARI_USER`, `ARI_PASS`, `ARI_APP` in `.env`.

ARI specifics vary across Asterisk 16/18/20 — treat this as a strong skeleton to verify against your deployed version.

---

## Service Management

```bash
# Start FreeSWITCH stack
docker compose --profile freeswitch up -d --build

# Stop
docker compose down

# Logs
docker compose logs -f

# Run Asterisk transport directly
python bot/server_asterisk.py
```

---

## Security

- `.env` is gitignored by default. Rotate any API key that appears in shell history.
- Containers run with default user contexts unless overridden in `bot/Dockerfile`.
- Dialplan and ARI paths should be restricted to internal/VPN networks where possible.
- Treat the `API_KEY`, `OLLAMA_HOST`, and `LLAMACPP_HOST` values as secrets: they grant model access or spend.

---

## Performance

- **STT throughput**: `WHISPER_DEVICE=cuda` is strongly preferred for sub-second latency on modern GPUs.
- **TTS latency**: Piper ONNX is low-latency; voice selection affects speed.
- **LLM latency**: local Ollama or llama.cpp on GPU will outperform hosted APIs for short prompts; hosted APIs are simpler to operate for high availability.
- **RTP/jitter**: low-latency paths benefit from low-jitter LAN links between PBX and bot.

---

## Troubleshooting

| Symptom | Check |
|---|---|
| No audio after dialing `8500` | `docker compose logs` for FreeSWITCH; confirm SIP attachment and codec match |
| STT silent or garbled | Verify `WHISPER_DEVICE`, model download, and 8kHz vs 16kHz `SAMPLE_RATE` |
| TTS silent | Confirm `PIPER_VOICE` path exists inside the bot runtime |
| LLM errors | Check backend logs for Ollama/llama.cpp/API base URL and auth |
| ARI 404 / auth failures | Confirm `ari.conf`, `http.conf`, and app name match `.env` |

---

## Known Limitations

- **VAD is amplitude-threshold based**, not real VAD — works well in quiet rooms, struggles with background noise. Swap in `webrtcvad` or `silero-vad` for production.
- **No barge-in** — caller can’t interrupt mid-response yet.
- **Sample rate**: FreeSWITCH path defaults to 8kHz (G.711); Asterisk defaults to 16kHz (slin16). Adjust `SAMPLE_RATE` to match your codec.
- **RTP framing** in `server_asterisk.py` is simplified — production should track sequence numbers/timestamps rather than stripping the 12-byte header.
- **No persistent memory across calls** — each call starts fresh. Wire transcripts into Honcho/Obsidian if you want call history.
- **Minimal error recovery** — STT/LLM/TTS failure mid-call stops audio rather than recovering gracefully.

---

## Roadmap

- Replace amplitude VAD with `silero-vad`
- Add barge-in (cut playback on caller speech)
- Stream LLM responses + Piper sentence-by-sentence to reduce perceived latency
- Persist call history to Honcho/Obsidian
- Improve error handling and graceful recovery

---

## Project Structure

```
hermes-voice/
├── bot/
│   ├── hermes_brain.py           # STT → LLM → TTS core
│   ├── server.py                 # FreeSWITCH transport
│   ├── server_asterisk.py        # Asterisk ARI transport
│   ├── persona.txt               # System prompt persona
│   ├── requirements.txt
│   └── Dockerfile
├── freeswitch/
│   └── conf/
│       └── dialplan/
│           └── hermes.xml        # FreeSWITCH dialplan
├── docker-compose.yml
├── .env.example
├── .gitignore
├── LICENSE
└── README.md
```

---

## Contributing

1. Create a feature branch off `master`.
2. Test on both FreeSWITCH and Asterisk if touching transports.
3. Keep secrets out of logs; update docs when env vars change.
4. Submit a PR with description and call audio/log snippets for voice/flow changes.

---

## License

MIT

---

## Author

Built by **Jhonattan L. Jimenez**.
