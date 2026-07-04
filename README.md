<div align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white">
  <img src="https://img.shields.io/badge/FreeSWITCH-063E55?style=for-the-badge&logo=freeswitch&logoColor=white">
  <img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white">
  <img src="https://img.shields.io/badge/Ollama-000?style=for-the-badge&logo=ollama&logoColor=white">
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
    <a href="#-integrations">Integrations</a>
  </p>
</div>

---

## ✨ Features

- **Phone Integration** — Works with FreeSWITCH, Asterisk/FreePBX, 3CX
- **Real-Time Pipeline** — Audio input → VAD → STT → LLM → TTS → Audio output
- **Local AI** — STT with faster-whisper, TTS with Piper, LLM with Ollama/llama.cpp
- **Containerized** — Docker Compose deployment
- **Transport-Agnostic** — Works with SIP, WebRTC, and more
- **GPU Support** — CUDA acceleration for STT and LLM

## 🚀 Quick Start

```bash
git clone https://github.com/OneByJorah/hermes-voice.git
cd hermes-voice
# Configure your .env file
docker-compose up -d
```

## 🏗️ Architecture

```
hermes-voice/
├── bot/                       # Core AI bot logic
│   ├── ...                    # STT, LLM, TTS modules
├── freeswitch/                # FreeSWITCH telephony config
├── docker-compose.yml         # Main deployment
└── README.md
```

### Pipeline
```
Caller → PBX → VAD → faster-whisper (STT) → LLM (Ollama/llama.cpp) → Piper (TTS) → Audio → Caller
```

## 📡 Integrations

| Platform | Type | Description |
|----------|------|-------------|
| FreeSWITCH | PBX | Bundled, full control |
| Asterisk/FreePBX | PBX | ARI integration |
| 3CX | PBX | SIP trunk support |
| Ollama | LLM | Local LLM inference |
| llama.cpp | LLM | Local LLM inference |
| faster-whisper | STT | Local speech-to-text |
| Piper | TTS | Local text-to-speech |

## 📄 License

MIT © Jhonattan L. Jimenez

---

<div align="center">
  <p>📞 Your AI assistant, on the phone</p>
  <p><a href="https://github.com/OneByJorah">@OneByJorah</a></p>
</div>
