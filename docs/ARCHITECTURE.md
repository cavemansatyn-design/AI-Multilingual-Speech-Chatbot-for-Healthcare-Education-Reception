# Architecture

## Overview

The Multilingual Speech Chatbot follows a **modular layered architecture**:

- **Client** — Streamlit UI (`ui_app.py`), CLI (`demo/cli_chatbot.py`), or API clients
- **API layer** (`api/`) — HTTP routes and request/response handling
- **Application layer** (`app/`) — Config, dependencies, FastAPI app bootstrap
- **Business logic** (`services/`) — NLP, ASR, TTS, translation, reports, security
- **Data layer** (`database/`, `models/`) — Persistence and domain models
- **Shared utilities** (`utils/`) — Text processing, constants

## Module Separation

| Module | Responsibility |
|--------|----------------|
| `api/` | REST endpoints; delegates to services |
| `app/` | Configuration, dependency injection, lifespan |
| `models/` | Pydantic schemas (user, symptom, report) |
| `services/` | Core logic: NLP, ASR, TTS, translation, report, PDF, auth |
| `database/` | MongoDB connection and CRUD |
| `utils/` | Stateless helpers and constants |
| `data/` | Static data (e.g. symptom list) |
| `demo/` | CLI and demo scripts |
| `tests/` | Unit and integration tests |

## Data Flow

1. **Text/audio input** → Streamlit UI or API validates and forwards to services.
2. **Translation** (if needed) → Input translated to English for NLP.
3. **NLP** → Symptom extraction or follow-up state update.
4. **Report** → Structured data turned into natural language; PDF generated on request.
5. **Translation** → Response translated to user language.
6. **TTS** (optional) → Audio generated and returned (e.g. base64).
7. **Persistence** (optional) → Users, patients, reports stored in MongoDB.

## Diagrams

- [System architecture](../assets/diagrams/architecture.svg) — High-level components
- [Speech processing pipeline](../assets/diagrams/speech-pipeline.svg) — ASR → NLP → TTS flow
- [API workflow](../assets/diagrams/api-workflow.svg) — Request/response and auth flow

Replace the placeholder SVGs in `assets/diagrams/` with your own diagrams when ready.
