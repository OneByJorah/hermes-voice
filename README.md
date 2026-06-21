# Hermes Voice — self-hosted phone-call AI assistant

Talk to a self-hosted Hermes agent over a real phone call. Bring your own PBX
(3CX, FreePBX, Asterisk, or the bundled FreeSWITCH) and your own LLM backend
(Ollama, llama.cpp, or a hosted API).

## Stack

- **Telephony transport** — FreeSWITCH (bundled, default) or Asterisk/FreePBX (`server_asterisk.py`); 3CX trunks into either
- **hermes_brain.py** — shared STT (faster-whisper, GPU) -> LLM -> TTS (Piper) core, used by both transports
- **LLM backend** — Ollama / llama.cpp / hosted API (Anthropic or OpenAI-compatible), switchable via `.env`

## Quick start

```bash
cp .env.example .env        # edit LLM_BACKEND and related vars
mkdir -p piper-voices && cd piper-voices
curl -LO https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/amy/medium/en_US-amy-medium.onnx
curl -LO https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/amy/medium/en_US-amy-medium.onnx.json
cd ..
docker compose --profile freeswitch up -d --build
```

Register a softphone against the bundled FreeSWITCH and dial **8500**.

## LLM backends

Set `LLM_BACKEND` in `.env` to one of:

| Backend | Use when | Key vars |
|---|---|---|
| `ollama` | Local model on your GPU box (default) | `OLLAMA_HOST`, `OLLAMA_MODEL` |
| `llamacpp` | Running `llama-server` directly off a GGUF | `LLAMACPP_HOST` |
| `api` | Hosted model (Anthropic or OpenAI-compatible) | `API_PROVIDER`, `API_BASE_URL`, `API_MODEL`, `API_KEY` |

All three speak through the same `ask_llm()` in `bot/hermes_brain.py` — switching is just an env var, no code changes needed. `llamacpp` expects `llama-server`'s OpenAI-compatible `/v1/chat/completions` endpoint already running (`llama-server -m model.gguf --port 8080`). `api` with `API_PROVIDER=openai` works for OpenAI, OpenRouter, or any OpenAI-schema gateway too.

## PBX options

All four route into the same `hermes_brain.py` core — only the audio transport differs.

### 1. Bundled FreeSWITCH (default, simplest)
Use as-is via `docker compose --profile freeswitch up`. Dial extension `8500`.

### 2. Keep your existing 3CX
1. Create a **SIP trunk** in 3CX pointing at the FreeSWITCH box's IP:5060.
2. Route a spare extension or DID to dial out over that trunk to `8500`.
3. 3CX keeps handling PSTN/SBC duties; FreeSWITCH + the bot handle the AI bridging. (3CX doesn't expose raw-media hooks the way FreeSWITCH/Asterisk do, so trunking into one of those is the practical path rather than running the bot logic inside 3CX itself.)

### 3. FreePBX
Same trunk pattern as 3CX — FreePBX is Asterisk under the hood, so you can either:
- Trunk a DID/extension from FreePBX into the bundled FreeSWITCH (identical to the 3CX path), **or**
- Use FreePBX's own Asterisk directly with `server_asterisk.py` (see below) and skip FreeSWITCH entirely.

### 4. Asterisk (standalone or via FreePBX) — `server_asterisk.py`
Uses Asterisk's **ARI + externalMedia** instead of FreeSWITCH's `mod_audio_fork`:
1. Enable ARI (`ari.conf`) and the built-in HTTP server (`http.conf`).
2. Add a dialplan extension that runs `Stasis(hermes-voice)` for your bot extension.
3. Run `python bot/server_asterisk.py` (set `ARI_HOST`, `ARI_USER`, `ARI_PASS`, `ARI_APP` in `.env`).

Full inline comments and setup steps are in `bot/server_asterisk.py`'s docstring. ARI specifics (channel/bridge behavior) vary a bit across Asterisk 16/18/20, so treat it as a strong skeleton to verify against your installed version's ARI docs rather than a drop-in.

## Known rough edges

- **VAD is amplitude-threshold based**, not real VAD — works in a quiet room, will misfire with background noise. Swap in `webrtcvad` or `silero-vad` for reliability.
- **No barge-in** — caller can't interrupt Hermes mid-response yet.
- **Sample rate**: FreeSWITCH path defaults to 8kHz (G.711); Asterisk path defaults to 16kHz (slin16). Adjust `SAMPLE_RATE` in `.env` to match your actual negotiated codec.
- **`server_asterisk.py`'s RTP framing is simplified** — a production version should track RTP sequence numbers/timestamps properly rather than just stripping the 12-byte header.
- **No persistent conversation memory across calls** — each call starts fresh. Easy to wire into your Honcho/Obsidian stack if you want call history.
- **Minimal error handling** — an STT/LLM/TTS failure mid-call currently just stops responding rather than recovering gracefully.

## Next steps worth doing
- Swap amplitude VAD for `silero-vad`
- Add barge-in (cut Piper playback the instant new caller speech is detected)
- Pipe call transcripts into Honcho/Obsidian for a call log
- Stream Ollama/llama.cpp responses + stream Piper sentence-by-sentence to cut perceived latency
