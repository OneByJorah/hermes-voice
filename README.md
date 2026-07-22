<div align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white">
  <img src="https://img.shields.io/badge/WebSocket-4CAF50?style=for-the-badge&logo=socket.io&logoColor=white">
  <img src="https://img.shields.io/badge/license-MIT-blue?style=for-the-badge">
  <img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white">
</div>

<br>

<div align="center">
  <h1>VoiceCortex</h1>
  <p><strong>Self-Hosted Phone AI Assistant</strong></p>
  <p>Real-time voice conversations over telephone via STT > LLM > TTS pipeline.</p>
  <p>
    <a href="#features">Features</a> •
    <a href="#quick-start">Quick Start</a> •
    <a href="#architecture">Architecture</a> •
    <a href="#contributing">Contributing</a>
  </p>
</div>

---

## Screenshot

![VoiceCortex Dashboard](docs/screenshot.png)
*Phone AI assistant with real-time voice conversations.*

## Features

- **Phone Integration** —接听电话并进行语音对话.
- **STT Pipeline** — Speech-to-text with faster-whisper.
- **LLM Processing** — AI-powered conversation with local/cloud LLMs.
- **TTS Output** — Natural speech synthesis with Piper.
- **Real-Time** — Low-latency WebSocket streaming.
- **Call Logging** — Record and transcribe all calls.
- **Multi-Provider** — Twilio, Asterisk, and SIP support.
- **Docker Ready** — Easy deployment with Docker.

## Quick Start

```bash
git clone https://github.com/OneByJorah/VoiceCortex.git
cd VoiceCortex

cp .env.example .env
docker compose up -d
```

### Local Development

```bash
pip install -r requirements.txt
python3 voicecortex.py
```

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `STT_PROVIDER` | `faster-whisper` | Speech-to-text provider |
| `STT_MODEL` | `base` | STT model size |
| `LLM_PROVIDER` | `ollama` | LLM provider |
| `LLM_MODEL` | `llama2` | LLM model name |
| `TTS_PROVIDER` | `piper` | Text-to-speech provider |
| `TTS_VOICE` | `en_US-lessac` | TTS voice |
| `TWILIO_SID` | — | Twilio account SID |
| `TWILIO_TOKEN` | — | Twilio auth token |
| `PORT` | `8080` | API port |

## Architecture

```
Phone Call ──▶ VoiceCortex ──▶ STT ──▶ LLM ──▶ TTS ──▶ Phone Response
                    │
                    ├──▶ faster-whisper
                    ├──▶ Ollama/OpenAI
                    ├──▶ Piper
                    └──▶ Call Logger
```

## Project Structure

```
VoiceCortex/
├── voicecortex.py          # Main entry point
├── pipeline/
│   ├── __init__.py
│   ├── stt.py              # Speech-to-text
│   ├── llm.py              # Language model
│   ├── tts.py              # Text-to-speech
│   └── phone.py            # Phone integration
├── providers/
│   ├── twilio.py           # Twilio integration
│   ├── asterisk.py         # Asterisk integration
│   └── sip.py              # SIP protocol
├── docker-compose.yml      # Docker deployment
├── requirements.txt        # Python dependencies
└── README.md
```

## Contributing

Contributions are welcome. Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines and [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) for community standards.

## Security

For security concerns, see [SECURITY.md](SECURITY.md). Please report vulnerabilities to **info@jorahone.com** — do not use public issues.

## License

MIT © Jhonattan L. Jimenez

---

<div align="center">
  <p>Self-hosted phone AI assistant.</p>
  <p><a href="https://github.com/OneByJorah">@OneByJorah</a></p>
</div>
