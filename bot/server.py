"""
Hermes Voice — FreeSWITCH transport
JorahOne

Accepts a WebSocket audio stream from FreeSWITCH (mod_audio_fork) and runs
it through hermes_brain.py (STT -> LLM -> TTS), streaming synthesized audio
back into the same call.

For Asterisk/FreePBX instead of FreeSWITCH, see server_asterisk.py — same
brain, different transport.
"""

import asyncio
import json
import os

import numpy as np
import websockets

import hermes_brain as brain

BOT_WS_PORT = int(os.environ.get("BOT_WS_PORT", "8765"))
SAMPLE_RATE = int(os.environ.get("SAMPLE_RATE", "8000"))  # 8000=G.711, 16000=wideband
SILENCE_MS = 700
SILENCE_THRESHOLD = 500


class CallSession:
    def __init__(self, call_id: str):
        self.call_id = call_id
        self.history = brain.new_history()
        self.buffer = bytearray()
        self.silence_ms = 0

    def reset_buffer(self):
        self.buffer = bytearray()
        self.silence_ms = 0


async def handle_connection(websocket):
    call_id = "unknown"
    session = None
    print("[hermes] new call connected")

    try:
        async for message in websocket:
            if isinstance(message, str):
                try:
                    meta = json.loads(message)
                    call_id = meta.get("call_id", "unknown")
                    session = CallSession(call_id)
                    print(f"[hermes] call_id={call_id} started")
                except json.JSONDecodeError:
                    pass
                continue

            if session is None:
                session = CallSession(call_id)

            session.buffer.extend(message)

            chunk = np.frombuffer(message, dtype=np.int16)
            is_silent = np.abs(chunk).mean() < SILENCE_THRESHOLD if len(chunk) else True
            frame_ms = (len(message) / 2) / SAMPLE_RATE * 1000

            session.silence_ms = session.silence_ms + frame_ms if is_silent else 0

            if session.silence_ms >= SILENCE_MS and len(session.buffer) > SAMPLE_RATE:
                pcm = bytes(session.buffer)
                session.reset_buffer()

                text = brain.transcribe(pcm, SAMPLE_RATE)
                if not text:
                    continue

                print(f"[hermes] [{call_id}] caller said: {text}")
                session.history.append({"role": "user", "content": text})

                reply = brain.ask_llm(session.history)
                session.history.append({"role": "assistant", "content": reply})
                print(f"[hermes] [{call_id}] hermes says: {reply}")

                audio_out = brain.synthesize_piper(reply, SAMPLE_RATE)

                frame_size = 320  # 20ms @ 8kHz mono PCM16
                for i in range(0, len(audio_out), frame_size):
                    await websocket.send(audio_out[i:i + frame_size])

    except websockets.exceptions.ConnectionClosed:
        print(f"[hermes] call_id={call_id} disconnected")


async def main():
    print(f"[hermes] FreeSWITCH bridge listening on 0.0.0.0:{BOT_WS_PORT}")
    async with websockets.serve(handle_connection, "0.0.0.0", BOT_WS_PORT, max_size=None):
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
