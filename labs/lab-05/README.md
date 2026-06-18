# Lab 05 — AI Agenci z LangChain

Agent AI to model LLM z dostępem do narzędzi, który samodzielnie decyduje, które narzędzie wywołać, aby rozwiązać zadanie.

## Zawartość

```
lab-05/
├── tutorial.md              ← przewodnik krok po kroku (15 sekcji)
└── solution/
    ├── tools.py             ← narzędzia agenta (calculator, time, knowledge base)
    ├── memory.py            ← pamięć rozmowy: InMemory + SQLite
    ├── app.py               ← agent z ręczną pętlą (wersja edukacyjna)
    └── agent_memory.py      ← agent create_agent z pamięcią (LangChain v1)
```

## Jak uruchomić

```bash
source .venv/bin/activate

# Wersja edukacyjna — widać każdy krok pętli agentowej
python labs/lab-05/solution/app.py

# Agent create_agent (LangChain v1) z pamięcią InMemory lub SQLite
python labs/lab-05/solution/agent_memory.py
```

## Narzędzia agenta

- `calculator` — bezpieczne obliczenia matematyczne,
- `get_current_time` — aktualna data i godzina,
- `search_knowledge_base` — wyszukiwanie pojęć w lokalnej bazie wiedzy.

## Przykładowe pytania

- `Ile to jest 145 * 23 + 17?` → użyje `calculator`
- `Która jest godzina?` → użyje `get_current_time`
- `Czym jest RAG?` → użyje `search_knowledge_base`
- `Podaj aktualną godzinę i policz 7 do potęgi 3` → użyje **dwóch** narzędzi

## Dwie wersje — po co?

- **app.py** pokazuje, co dzieje się "pod maską": model wybiera narzędzie → kod je wykonuje → wynik wraca do modelu. Świetne do zrozumienia mechanizmu.
- **agent_memory.py** to podejście zgodne z LangChain 1.0 — agent tworzony funkcją `create_agent`, z pamięcią rozmowy w dwóch wariantach:
  - **InMemory** — szybka, ulotna pamięć w RAM,
  - **SQLite** — trwała pamięć w pliku `agent_memory.db`, która przeżywa restart.

Po uruchomieniu `agent_memory.py` wybierz backend pamięci. Aby zobaczyć działanie pamięci, przedstaw się agentowi, a w kolejnej wiadomości zapytaj go o swoje imię.

Wymagany jest ustawiony `OPENAI_API_KEY` oraz pakiety z `requirements.txt`.
