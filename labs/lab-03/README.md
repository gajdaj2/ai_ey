# Lab 03 — Streamlit + LangChain + OpenAI

Prosty asystent AI w formie aplikacji czatowej.

## Zawartość

- `tutorial.md` — przewodnik krok po kroku,
- `solution/app.py` — gotowa aplikacja Streamlit.

## Jak uruchomić

```bash
source .venv/bin/activate
streamlit run labs/lab-03/solution/app.py
```

Aplikacja otworzy się automatycznie w przeglądarce pod `http://localhost:8501`.

## Funkcje aplikacji

- historia rozmowy z pamięcią w sesji,
- strumieniowanie odpowiedzi modelu,
- konfigurowalny prompt systemowy,
- wybór modelu i temperatury przez panel boczny,
- przycisk czyszczenia historii.

Wymagany jest ustawiony `OPENAI_API_KEY`.
