# Lab 04 — RAG z LangChain i ChromaDB

Pipeline Retrieval-Augmented Generation — odpowiedzi z lokalnej bazy wiedzy z cytowaniem źródeł.

## Zawartość

```
lab-04/
├── tutorial.md          ← przewodnik krok po kroku
├── data/
│   └── baza_wiedzy.txt  ← przykładowa baza dokumentów
└── solution/
    ├── app.py           ← gotowa aplikacja RAG
    └── chroma_db/       ← tworzy się automatycznie przy pierwszym uruchomieniu
```

## Jak uruchomić

```bash
source .venv/bin/activate
python labs/lab-04/solution/app.py
```

Przy pierwszym uruchomieniu aplikacja:
1. wczyta `data/baza_wiedzy.txt`,
2. podzieli tekst na chunki,
3. wygeneruje embeddingi przez OpenAI,
4. zapisze bazę wektorową lokalnie w `solution/chroma_db/`.

Przy kolejnych uruchomieniach baza jest wczytywana z dysku — bez kosztów API za embeddingi.

## Przykładowe pytania

- `Czym jest LangChain?`
- `Jak działa RAG?`
- `Co to są embeddingi?`
- `Jak działa ChromaDB?`
- `Jak łączyć Streamlit z RAG?`

## Wymagania

Ustawiony `OPENAI_API_KEY` oraz pakiety z `requirements.txt`.
