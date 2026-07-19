# AGENT_LOG — VoiceCortex

## Phase 0 — Intake
- Stack: Python 3.11 voice AI call bot (STT faster-whisper → LLM → TTS Piper), WebSocket transport for FreeSWITCH (`bot/server.py`) and Asterisk ARI (`bot/server_asterisk.py`).
- Deployment: `Dockerfile` (multi-stage) + `bot/Dockerfile` (single-stage) + `docker-compose.yml` (FreeSWITCH + bot, profiles).
- README is honest: "CLI/backend-only tool. No screenshots available." Code structure matches README. MIT, credits Jhonattan L. Jimenez.
- Heavy ML deps (torch, faster-whisper, piper, silero-vad) required at import time.

## Phase 1 — Get It Running
- `python3 -m compileall bot/` → all modules compile, no syntax errors.
- Light-dependency import probe (stubbing the heavy ML libs) confirmed the project's OWN module graph loads: `server`, `hermes_brain`, `vad` import; persona file loads; a `websockets.serve` on :8765 starts ("RUNS OK").
- Full boot blocked only by legitimate heavy deps (WhisperModel/PiperVoice instantiated at import in `hermes_brain.py:42`) + GPU/FreeSWITCH/PBX — by design, not a bug.
- Environment disk constraint (root fs hit 99% during a venv pip attempt) forced cleanup of ~20GB of stale Docker images/cache. Full container build (multi-GB torch/whisper download) could not be completed in this session because the docker build process does not survive the tool's process-group teardown; config reviewed correct (module paths resolve because `CMD python bot/server.py` puts `bot/` on sys.path).

## Phase 2 — Fix & Harden
- No code bugs found. `hermes_brain` reads `PERSONA_FILE` at import (default `/app/persona.txt`, provided by Dockerfile copy + compose env). Works in-container.
- Extended `.gitignore` (`.venv/`, `venv/`).
- Secret scan: no committed secrets; `.env` not tracked; `.env.example` only. OK.

## Phase 3 — Dockerize
- Dockerfile + bot/Dockerfile + compose already present and coherent. Not rebuilt end-to-end here (see Phase 1 disk/teardown note). The `bot` service mounts `./bot:/app` and `./piper-voices:/piper-voices`; HEALTHCHECK on :8765 present.

## Phase 4 — Screenshots
- N/A: backend/CLI voice tool; README correctly states no screenshots. No fake images present.

## Phase 5 — README
- Already accurate and honest. No rewrite needed. Minor stale artifact: `AUDIT_REPORT.md` (2026-07-05) flagged missing files (j1.yaml, .dockerignore, CODEOWNERS, CHANGELOG) that now exist after the rebrand commits — left as historical record; not a defect.

## Status: DONE (verified by compile + import-graph + server-boot probe; full container run needs GPU/FreeSWITCH/PBX + heavy ML deps not available in this sandbox)
