<div align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white">
  <img src="https://img.shields.io/badge/FreeSWITCH-063E55?style=for-the-badge&logo=freeswitch&logoColor=white">
  <img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white">
  <img src="https://img.shields.io/badge/Ollama-000?style=for-the-badge&logo=ollama&logoColor=white">
  <img src="https://img.shields.io/badge/license-MIT-blue?style=for-the-badge">
</div>

<br>

<div align="center">
  <h1>📞 Hermes Voice</h1>
  <p><strong>Self-Hosted Phone AI Assistant</strong></p>
  <p>Real-time AI-powered voice conversations over telephone — STT → LLM → TTS pipeline</p>
  <p>
    <a href="#-features">Features</a> •
    <a href="#-quick-start">Quick Start</a> •
    <a href="#-architecture">Architecture</a> •
    <a href="#-configuration">Configuration</a> •
    <a href="#-pbx-integration">PBX Integration</a> •
    <a href="#-troubleshooting">Troubleshooting</a>
  </p>
</div>

---

## 📸 Screenshot

This is a CLI/backend-only tool. No screenshots available.

## ✨ Features

- **📞 Phone Integration** — Works with FreeSWITCH, Asterisk/FreePBX, and 3CX
- **🔊 Real-Time Pipeline** — Audio input → VAD → STT → LLM → TTS → Audio output
- **🤖 Local AI Stack** — faster-whisper (STT), Ollama/llama.cpp (LLM), Piper (TTS) — all run locally
- **🐳 Containerized** — One-command Docker Compose deployment
- **🔄 Transport-Agnostic** — Same brain core works with FreeSWITCH WebSocket or Asterisk ARI
- **🎮 GPU Accelerated** — CUDA support for STT and optional LLM GPU inference
- **☁️ Hybrid Mode** — Use local STT/TTS with a hosted LLM API (Anthropic, OpenAI, OpenRouter)

---

## 🏗️ Architecture

```
                    ┌──────────────────────────────────────────────────┐
                    │               Hermes Voice Stack                │
                    │                                                  │
Caller  ──SIP/RTP──▶│  PBX Layer (pick one)                           │
                    │  ├── FreeSWITCH  (bundled, default)             │
                    │  ├── Asterisk/FreePBX  (ARI + externalMedia)    │
                    │  └── 3CX  (SIP trunk)                          │
                    │          │                                       │
                    │          ▼                                       │
                    │  ┌────────────────┐                             │
                    │  │  hermes_brain  │                             │
                    │  │  ┌──────────┐  │                             │
                    │  │  │   VAD    │  │  (amplitude-based)          │
                    │  │  ├──────────┤  │                             │
                    │  │  │   STT    │  │  faster-whisper             │
                    │  │  ├──────────┤  │                             │
                    │  │  │   LLM    │  │  Ollama / llama.cpp / API   │
                    │  │  ├──────────┤  │                             │
                    │  │  │   TTS    │  │  Piper ONNX                 │
                    │  │  └──────────┘  │                             │
                    │  └────────────────┘                             │
                    └──────────────────────────────────────────────────┘
```

### Pipeline (per call)

`Audio in → VAD detects speech → STT transcribes → LLM thinks → TTS speaks → Audio out`

---

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose v2
- Ollama running locally (or another LLM backend)
- A Piper voice model (see below)
- (Optional) FreeSWITCH for the bundled telephony path

### 1. Clone & configure

```bash
git clone https://github.com/OneByJorah/VoiceCortex.git
cd VoiceCortex
cp .env.example .env
# Edit .env for your LLM backend and paths
```

### 2. Download a Piper voice

```bash
mkdir -p piper-voices
curl -LO https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/amy/medium/en_US-amy-medium.onnx
curl -LO https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/amy/medium/en_US-amy-medium.onnx.json
```

### 3. Start the stack

```bash
# With FreeSWITCH (bundled PBX):
docker compose --profile freeswitch up -d --build

# Without FreeSWITCH (bring your own PBX):
docker compose up -d --build
```

### 4. Call the bot

Dial extension **8500** from any SIP phone registered to your PBX.

---

## 🔧 Configuration

Copy `.env.example` to `.env` and set the variables for your chosen backend.

### LLM Backend

| Variable | Default | Description |
|----------|---------|-------------|
| `LLM_BACKEND` | `ollama` | One of: `ollama`, `llamacpp`, `api` |
| `OLLAMA_HOST` | `http://127.0.0.1:11434` | Ollama server URL |
| `OLLAMA_MODEL` | `llama3.1:8b-instruct-q4_K_M` | Ollama model name |
| `LLAMACPP_HOST` | `http://127.0.0.1:8080` | llama.cpp server URL (OpenAI-compat) |
| `API_PROVIDER` | `anthropic` | Hosted API provider: `anthropic` or `openai` |
| `API_BASE_URL` | `https://api.anthropic.com/v1/messages` | API endpoint URL |
| `API_MODEL` | `claude-sonnet-4-6` | Model name for hosted API |
| `API_KEY` | — | API key for hosted provider |

### Speech

| Variable | Default | Description |
|----------|---------|-------------|
| `WHISPER_MODEL` | `small.en` | Model size: `base.en`, `small.en`, or `medium.en` |
| `WHISPER_DEVICE` | `cuda` | `cuda` or `cpu` |
| `PIPER_VOICE` | `/piper-voices/en_US-amy-medium.onnx` | Path to Piper ONNX voice file |
| `VAD_BACKEND` | `auto` | Backend: `auto` (Silero if PyTorch available), `amplitude` (force fallback) |
| `SAMPLE_RATE` | `8000` | Audio sample rate (8000 for G.711, 16000 for wideband) |

### Server

| Variable | Default | Description |
|----------|---------|-------------|
| `BOT_WS_PORT` | `8765` | WebSocket port for bot server |

---

## 📡 PBX Integration

### FreeSWITCH (default)

```bash
docker compose --profile freeswitch up -d --build
```

Dial `8500` from any SIP phone. The bundled FreeSWITCH handles the call and streams audio to the bot via `mod_audio_fork`.

### 3CX

1. Create a SIP trunk in 3CX pointing at your FreeSWITCH host on port `5060`
2. Route a DID or extension to dial `8500` over that trunk
3. Start the stack without FreeSWITCH (or let it coexist)

### FreePBX / Asterisk — ARI transport

1. Enable ARI in `ari.conf` and HTTP in `http.conf`
2. Add a dialplan extension that runs `Stasis(voicecortex)`
3. Set `ARI_HOST`, `ARI_USER`, `ARI_PASS`, `ARI_APP` in `.env`
4. Run `python bot/server_asterisk.py` instead of the FreeSWITCH server

```bash
# Example extensions.conf entry
exten => 8500,1,NoOp(Hermes Voice)
 same => n,Answer()
 same => n,Stasis(voicecortex)
 same => n,Hangup()
```

> **Note:** ARI behavior differs slightly across Asterisk 16/18/20. Treat `server_asterisk.py` as a strong starting point to adapt to your version.

---

## 🐳 Docker Compose

### Start with FreeSWITCH

```bash
docker compose --profile freeswitch up -d --build
```

### Start bot only (bring your own PBX)

```bash
docker compose up -d --build
```

### Include Ollama in the stack

Uncomment the `ollama` service in `docker-compose.yml` and:

```bash
docker compose --profile freeswitch -f docker-compose.yml up -d --build
```

### View logs

```bash
docker compose logs -f
```

---

## 🛠️ Troubleshooting

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| No audio after dialing `8500` | FreeSWITCH not running or SIP not registered | Check `docker compose logs freeswitch`; confirm SIP phone is registered |
| STT returns empty/silence | Whisper model not downloaded or wrong device | Verify `WHISPER_MODEL` is downloaded; switch `WHISPER_DEVICE=cpu` if no GPU |
| TTS produces no audio | Piper voice model not found in container | Ensure `PIPER_VOICE` path exists; voice must be in `./piper-voices/` |
| LLM returns errors | Backend not running or wrong host/port | Check Ollama: `curl http://127.0.0.1:11434/api/tags`; verify `OLLAMA_HOST` |
| API (hosted) fails | Missing or invalid API key | Set `API_KEY` in `.env`; verify `API_BASE_URL` and `API_MODEL` |
| Audio quality issues | Sample rate mismatch between codec and bot | Match `SAMPLE_RATE` in `.env` to your PBX codec (8000 for G.711, 16000 for slin16) |

---

## 🧠 Known Limitations

- **VAD** — Uses **Silero VAD** (deep learning) by default if PyTorch is available, with automatic fallback to amplitude-threshold VAD. Silero handles background noise much better. Force amplitude mode with `VAD_BACKEND=amplitude`.
- **No barge-in** — callers cannot interrupt mid-response yet.
- **No persistent memory across calls** — each call starts fresh. Wire transcripts into a vector store (e.g. Qdrant, Honcho) for call history.
- **Minimal error recovery** — STT/LLM/TTS failure mid-call stops audio rather than recovering gracefully.
- **RTP framing in Asterisk transport** — simplified; production should track RTP sequence numbers and timestamps.

---

## 🗺️ Roadmap

- [x] Replace amplitude VAD with Silero VAD
- [ ] Add barge-in (interrupt playback on caller speech)
- [ ] Stream LLM responses sentence-by-sentence to reduce latency
- [ ] Persist call history to Honcho / Qdrant / Obsidian
- [ ] Improved error recovery and graceful degradation
- [ ] WebRTC transport (browser-based calling)
- [ ] Multi-language support

---

## 📁 Project Structure

```
VoiceCortex/
├── bot/
│   ├── hermes_brain.py           # STT → LLM → TTS core (shared)
│   ├── server.py                 # FreeSWITCH WebSocket transport
│   ├── server_asterisk.py        # Asterisk ARI transport
│   ├── persona.txt               # System prompt / assistant persona
│   ├── Dockerfile
│   └── requirements.txt
├── freeswitch/
│   └── conf/
│       └── dialplan/
│           └── hermes.xml        # FreeSWITCH dialplan for extension 8500
├── .env.example                  # Template for environment variables
├── .gitignore
├── docker-compose.yml
├── LICENSE
└── README.md
```

---

## 📄 License

MIT © Jhonattan L. Jimenez

See [LICENSE](LICENSE) for full text.

---

<div align="center">
  <p>📞 Your AI assistant, on the phone</p>
  <p><a href="https://github.com/OneByJorah">@OneByJorah</a></p>
</div>
