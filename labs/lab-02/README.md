# Lab 02 — FastAPI + LangChain + OpenAI

Ten lab pokazuje, jak zbudować proste API HTTP w `FastAPI`, które wywołuje model OpenAI przez `LangChain`.

## Zawartość

- `tutorial.md` — przewodnik krok po kroku,
- `solution/app.py` — gotowa aplikacja API.

## Jak uruchomić

```bash
source .venv/bin/activate
uvicorn app:app --app-dir labs/lab-02/solution --reload
```

Po uruchomieniu otwórz:

- `http://127.0.0.1:8000/docs` — Swagger UI,
- `http://127.0.0.1:8000/health` — prosty endpoint health check.

Wymagany jest ustawiony `OPENAI_API_KEY`.
