# Lab 06 — Middleware w LangChain

Middleware to warstwy, które „opakowują” agenta i pozwalają wpinać logikę
oboczną (streszczanie, ochrona danych, limity, zgoda człowieka, ponowienia) bez
zmiany kodu samego agenta. Dodajesz je przez parametr `middleware=[...]` w
`create_agent`.

> Materiał źródłowy: [Prebuilt middleware](https://docs.langchain.com/oss/python/langchain/middleware/built-in).

## Zawartość

```
lab-06/
├── tutorial.md                  ← przewodnik krok po kroku (13 sekcji)
└── solution/
    ├── tools.py                 ← narzędzia współdzielone przez przykłady
    ├── 01_summarization.py      ← streszczanie długiej historii rozmowy
    ├── 02_pii_detection.py      ← ochrona danych wrażliwych (PII)
    ├── 03_call_limits.py        ← limity wywołań modelu i narzędzi
    ├── 04_human_in_the_loop.py  ← zgoda człowieka przed akcją
    ├── 05_tool_retry.py         ← automatyczne ponowienia narzędzi
    └── 06_combined.py           ← kilka middleware naraz
```

## Jak uruchomić

```bash
source .venv/bin/activate

python labs/lab-06/solution/01_summarization.py
python labs/lab-06/solution/02_pii_detection.py
python labs/lab-06/solution/03_call_limits.py
python labs/lab-06/solution/04_human_in_the_loop.py   # interaktywny: zatwierdź/odrzuć
python labs/lab-06/solution/05_tool_retry.py
python labs/lab-06/solution/06_combined.py
```

Wymagany jest ustawiony `OPENAI_API_KEY`, pakiety z `requirements.txt` oraz
**LangChain ≥ 1.0**.

## Omówienie przykładów

| Plik | Middleware | Co pokazuje |
|------|------------|-------------|
| `01_summarization.py` | `SummarizationMiddleware` | streszcza starsze wiadomości, gdy historia rośnie |
| `02_pii_detection.py` | `PIIMiddleware` | strategie `redact` / `mask` / `hash` / `block` dla e-maila, karty, IP |
| `03_call_limits.py` | `ModelCallLimitMiddleware`, `ToolCallLimitMiddleware` | twarde limity chroniące przed pętlą i kosztami |
| `04_human_in_the_loop.py` | `HumanInTheLoopMiddleware` | przerwanie i wznowienie biegu decyzją człowieka |
| `05_tool_retry.py` | `ToolRetryMiddleware` | ponowienia zawodnego narzędzia z backoffem |
| `06_combined.py` | cztery middleware naraz | składanie middleware w jednym agencie |

## Kluczowe pojęcia

- **Zaczepy (hooks):** middleware działa `before_model`, wokół modelu i
  `after_model` oraz wokół wywołań narzędzi.
- **Kolejność ma znaczenie:** middleware otaczają model jak warstwy cebuli —
  pierwsze na liście jest „najbardziej zewnętrzne”.
- **`checkpointer`:** wymagany tam, gdzie middleware operuje na stanie wątku
  (streszczanie, limity wątkowe, human-in-the-loop).
- **Typowanie list:** łącząc middleware o różnych typach stanu, otypuj listę
  jako `list[AgentMiddleware[Any, Any, Any]]`.

Szczegóły i wyjaśnienia krok po kroku znajdziesz w [tutorial.md](tutorial.md).
