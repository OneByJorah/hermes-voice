"""
Hermes Voice — shared brain
JorahOne

STT -> LLM -> TTS logic shared between transports (FreeSWITCH server.py,
Asterisk server_asterisk.py). Transport-specific files handle getting audio
in and out; this module only knows about PCM16 bytes and text.
"""

import io
import os

import numpy as np
import requests
import soundfile as sf
from faster_whisper import WhisperModel
from piper import PiperVoice
import wave

LLM_BACKEND = os.environ.get("LLM_BACKEND", "ollama")  # ollama | llamacpp | api

OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://127.0.0.1:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.1:8b-instruct-q4_K_M")

LLAMACPP_HOST = os.environ.get("LLAMACPP_HOST", "http://127.0.0.1:8080")

API_BASE_URL = os.environ.get("API_BASE_URL", "https://api.anthropic.com/v1/messages")
API_KEY = os.environ.get("API_KEY", "")
API_MODEL = os.environ.get("API_MODEL", "claude-sonnet-4-6")
API_PROVIDER = os.environ.get("API_PROVIDER", "anthropic")

WHISPER_MODEL = os.environ.get("WHISPER_MODEL", "small.en")
WHISPER_DEVICE = os.environ.get("WHISPER_DEVICE", "cuda")
PIPER_VOICE = os.environ.get("PIPER_VOICE", "/piper-voices/en_US-amy-medium.onnx")
PERSONA_FILE = os.environ.get("HERMES_SYSTEM_PROMPT_FILE", "/app/persona.txt")

with open(PERSONA_FILE) as f:
    SYSTEM_PROMPT = f.read().strip()

print(f"[hermes] LLM backend = {LLM_BACKEND}")
print(f"[hermes] loading whisper model={WHISPER_MODEL} device={WHISPER_DEVICE}")
whisper_model = WhisperModel(
    WHISPER_MODEL, device=WHISPER_DEVICE,
    compute_type="float16" if WHISPER_DEVICE == "cuda" else "int8",
)


def pcm16_to_wav_bytes(pcm_bytes: bytes, sample_rate: int) -> bytes:
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(pcm_bytes)
    return buf.getvalue()


def transcribe(pcm_bytes: bytes, sample_rate: int) -> str:
    audio_np = np.frombuffer(pcm_bytes, dtype=np.int16).astype(np.float32) / 32768.0
    segments, _ = whisper_model.transcribe(audio_np, language="en", vad_filter=True)
    return " ".join(seg.text.strip() for seg in segments).strip()


def ask_llm(history: list[dict]) -> str:
    if LLM_BACKEND == "ollama":
        return ask_ollama(history)
    elif LLM_BACKEND == "llamacpp":
        return ask_llamacpp(history)
    elif LLM_BACKEND == "api":
        return ask_api(history)
    raise ValueError(f"Unknown LLM_BACKEND: {LLM_BACKEND}")


def ask_ollama(history: list[dict]) -> str:
    resp = requests.post(
        f"{OLLAMA_HOST}/api/chat",
        json={"model": OLLAMA_MODEL, "messages": history, "stream": False},
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json()["message"]["content"].strip()


def ask_llamacpp(history: list[dict]) -> str:
    resp = requests.post(
        f"{LLAMACPP_HOST}/v1/chat/completions",
        json={"messages": history, "temperature": 0.7, "stream": False},
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"].strip()


def ask_api(history: list[dict]) -> str:
    if not API_KEY:
        raise RuntimeError("API_KEY is not set but LLM_BACKEND=api")

    if API_PROVIDER == "anthropic":
        system = next((m["content"] for m in history if m["role"] == "system"), "")
        messages = [m for m in history if m["role"] != "system"]
        resp = requests.post(
            API_BASE_URL,
            headers={
                "x-api-key": API_KEY,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={"model": API_MODEL, "max_tokens": 1000, "system": system, "messages": messages},
            timeout=60,
        )
        resp.raise_for_status()
        data = resp.json()
        return "".join(b["text"] for b in data["content"] if b["type"] == "text").strip()

    resp = requests.post(
        API_BASE_URL,
        headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
        json={"model": API_MODEL, "messages": history, "stream": False},
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"].strip()


def resample_pcm16(pcm_bytes: bytes, src_rate: int, dst_rate: int) -> bytes:
    if src_rate == dst_rate:
        return pcm_bytes
    audio = np.frombuffer(pcm_bytes, dtype=np.int16).astype(np.float32)
    duration = len(audio) / src_rate
    dst_len = int(duration * dst_rate)
    resampled = np.interp(
        np.linspace(0, len(audio), dst_len, endpoint=False),
        np.arange(len(audio)),
        audio,
    ).astype(np.int16)
    return resampled.tobytes()


def synthesize_piper(text: str, dst_sample_rate: int) -> bytes:
    """Runs Piper TTS via Python module, returns raw PCM16 @ dst_sample_rate bytes."""
    voice = PiperVoice.load(PIPER_VOICE)
    audio_bytes = io.BytesIO()
    voice.synthesize(text, audio_bytes)
    audio_bytes.seek(0)

    data, sr = sf.read(audio_bytes, dtype='float32')
    if sr != dst_sample_rate:
        data = np.interp(
            np.linspace(0, len(data), int(len(data) * dst_sample_rate / sr), endpoint=False),
            np.arange(len(data)),
            data,
        )
    return (data * 32767).astype(np.int16).tobytes()


def new_history() -> list[dict]:
    return [{"role": "system", "content": SYSTEM_PROMPT}]
