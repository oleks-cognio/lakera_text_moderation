## Content Moderation MVP

This repository contains an MVP service demonstrating local content moderation using a Hugging Face model, exposed via a FastAPI JSON API, with simple requests-per-second tracking and basic tests.

---

### 1. Overview

- **Model**: `KoalaAI/Text-Moderation` (Hugging Face)
- **Framework**: FastAPI
- **Inference**: Local, via `transformers` pipeline
- **Metrics**: Thread-pooled inference + stdout-logged timestamps + post-process RPS script
- **Testing**: Pytest + FastAPI TestClient + timestamp parser tests

---

### 2. Repository Structure

```
moderation-mvp/
├── app/
│   ├── __init__.py      # Makes app/ a package
│   └── main.py          # FastAPI app: endpoints, middleware, lifespan
├── model/
│   └── __init__.py      # Inference wrapper loading HF pipeline
├── scripts/
│   └── compute_rps.py   # Utility to compute RPS from logs
├── tests/
│   └── test_app.py      # Unit tests for endpoints and timestamp parser
├── run_demo.sh          # Demo script: start server, load test, compute RPS
├── requirements.txt     # Python dependencies (includes httpx, pytest)
├── .gitignore           # Common ignores: venv, bytecode, logs
├── README.md            # This file
└── moderation.log       # Generated log file (ignored)
```

---

### 3. Prerequisites

- Python 3.10+ (verified on 3.13)
- macOS/Linux shell (scripts assume a UNIX-like environment)

---

### 4. Setup & Installation

```bash
# Clone the repo
# git clone git@github.com:oleks-cognio/lakera_text_moderation.git
cd lakera_text_moderation

# Create & activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

### 5. Running the API

```bash
uvicorn app.main:app --reload
```

- **Health check**: GET `/healthz` → `{ "status": "ok" }`
- **Moderation**: POST `/moderate` with JSON `{ "text": "..." }` → `{ "not_offensive": 0.97, ... }`

Example:
```bash
curl -X POST http://127.0.0.1:8000/moderate \
     -H "Content-Type: application/json" \
     -d '{"text":"I hate spoilers!"}'
```

---

### 6. Demonstration Script

There are two ways to measure RPS from your service:

#### Manual Approach

1. **Start the server** in one terminal, capturing logs:
   ```bash
   uvicorn app.main:app --reload > moderation.log 2>&1
   ```
2. **In another terminal**, fire off concurrent requests:
   ```bash
   for i in {1..20}; do
     curl -s -X POST http://127.0.0.1:8000/moderate \
          -H "Content-Type: application/json" \
          -d '{"text":"test"}' &
   done
   wait
   ```
3. **Stop the server** (Ctrl+C in the first terminal).
4. **Compute RPS** by running:
   ```bash
   python scripts/compute_rps.py moderation.log
   ```

#### Automated Demo Script

A convenience script bundles all steps:

```bash
chmod +x run_demo.sh        # only once
./run_demo.sh               # runs server, load test, and RPS calc
```

At the end you’ll see output like:
```
2025-07-01T12:49:12: 20 req/s
```

---

### 7. Tests

We include simple pytest-based tests in `tests/test_app.py`:

- **`test_healthz_endpoint`**: Verifies the `/healthz` route returns status ok.
- **`test_moderate_endpoint`**: Stubs out the inference to verify `/moderate` returns expected JSON.
- **`test_parse_timestamps_empty`**: Ensures `parse_timestamps` returns an empty list for no input.
- **`test_parse_timestamps_valid`**: Confirms timestamp parser extracts valid datetime objects from mixed log lines.

Run the tests with:
```bash
pytest -q
```

---

### 8. Assumptions & Trade-offs

- **No external metrics**: stdout logs + post-processing vs. Prometheus.
- **Thread-pooled inference**: `run_in_threadpool` avoids blocking the event loop.
- **Model warm-up**: Dummy inference at startup via FastAPI lifespan.
- **No auth/rate-limit**: Simplified for MVP.

---

### 9. Production-MVP Roadmap

1. **Containerization**: Docker + Kubernetes/Fargate deployment
2. **Metrics & Observability**: Prometheus/Grafana, structured logs
3. **Scaling**: Batch inference, autoscaling, GPU support
4. **Reliability**: Health/readiness probes, retries, circuit breakers
5. **Security**: API keys/OAuth, input sanitization
6. **Model Lifecycle**: Versioning, A/B testing, continual retraining

---

**AI Assistance**

_Initial code scaffolding and README wording were informed by ChatGPT prompts; all final implementation and logic were reviewed and adjusted by me._

*Example prompt:*  
“Generate a FastAPI app skeleton with a lifespan-based startup warm-up, middleware for request timestamp logging, and a `/healthz` endpoint.”