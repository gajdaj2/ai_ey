# Lab 06 — Tutorial: Middleware w LangChain

## Cel labu

W tym labie poznasz **middleware** — warstwy, które „opakowują” agenta i pozwalają
wpinać się w jego cykl działania: przed wywołaniem modelu, po nim oraz wokół
wywołań narzędzi. Dzięki gotowym (wbudowanym) middleware dodasz agentowi
streszczanie historii, ochronę danych wrażliwych (PII), limity kosztów, zgodę
człowieka na akcje oraz automatyczne ponowienia — **bez zmiany logiki samego
agenta**.

Po wykonaniu labu uczestnik powinien umieć:

- wyjaśnić, czym jest middleware i jak osadza się w pętli agentowej,
- podpiąć wbudowane middleware przez parametr `middleware=[...]` w `create_agent`,
- użyć `SummarizationMiddleware` do streszczania długich rozmów,
- chronić dane wrażliwe za pomocą `PIIMiddleware`,
- ograniczyć koszty przez `ModelCallLimitMiddleware` i `ToolCallLimitMiddleware`,
- wstrzymać agenta po zgodę człowieka (`HumanInTheLoopMiddleware`),
- uodpornić narzędzia na chwilowe awarie (`ToolRetryMiddleware`),
- łączyć wiele middleware w jednym agencie.

> Lab bazuje na wiedzy z lab-05 (agenci `create_agent`, narzędzia `@tool`).
> Materiał źródłowy: [Prebuilt middleware](https://docs.langchain.com/oss/python/langchain/middleware/built-in).

---

## Wymagania

- Python 3.10+
- aktywne środowisko wirtualne,
- ustawiony `OPENAI_API_KEY`,
- zainstalowane pakiety z `requirements.txt` (wymagany **LangChain ≥ 1.0**).

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

Uruchomienie gotowych przykładów:

```bash
python labs/lab-06/solution/01_summarization.py
python labs/lab-06/solution/02_pii_detection.py
python labs/lab-06/solution/03_call_limits.py
python labs/lab-06/solution/04_human_in_the_loop.py
python labs/lab-06/solution/05_tool_retry.py
python labs/lab-06/solution/06_combined.py
```

---

## 1. Czym jest middleware?

W lab-05 agent działał w pętli: **model → narzędzie → obserwacja → model**.
Middleware to **warstwa pośrednicząca**, która pozwala wpiąć własną logikę w
kluczowych punktach tej pętli — nie dotykając kodu agenta ani narzędzi.

Analogia: middleware to jak **wtyczki/filtry** w serwerze HTTP. Każde żądanie
przechodzi przez łańcuch warstw (uwierzytelnianie, logowanie, kompresja), zanim
trafi do właściwego handlera — i z powrotem. Tutaj „żądaniem” jest wywołanie
modelu, a „warstwami” — middleware.

| Bez middleware | Z middleware |
|----------------|--------------|
| Logika obocza (limity, PII, retry) wmieszana w kod agenta | Każda troska w osobnej, wymiennej warstwie |
| Trudno włączyć/wyłączyć funkcję | Dodajesz/usuwasz pozycję z listy `middleware=[...]` |
| Powielanie kodu w wielu agentach | Jedno middleware reużywane wszędzie |

---

## 2. Gdzie middleware wpina się w pętlę agenta

Każde middleware może działać w kilku „zaczepach” (hooks) cyklu agenta:

```
        wiadomość użytkownika
                │
                ▼
   ┌───────────────────────────┐
   │  before_model             │  ← np. PII (sanityzacja wejścia),
   │                           │     streszczanie historii
   └───────────────────────────┘
                │
                ▼
           [  MODEL  ]            ← np. limit wywołań modelu, fallback, retry
                │
                ▼
   ┌───────────────────────────┐
   │  after_model              │  ← np. human-in-the-loop (przerwanie po
   │                           │     decyzji o wywołaniu narzędzia)
   └───────────────────────────┘
                │
                ▼
          [  NARZĘDZIE  ]         ← np. ToolRetry (ponowienia),
                │                    limit wywołań narzędzia
                ▼
            obserwacja ───────────► (z powrotem do modelu)
```

Najważniejsze: **nie musisz znać wnętrza tych zaczepów, żeby używać wbudowanych
middleware**. Wystarczy dodać je do listy `middleware`.

---

## 3. Jak podpiąć middleware

Middleware przekazujesz do `create_agent` przez parametr `middleware` — to lista,
więc można podać ich kilka:

```python
from langchain.agents import create_agent
from langchain.agents.middleware import SummarizationMiddleware

agent = create_agent(
    model,
    tools=[...],
    system_prompt="...",
    middleware=[
        SummarizationMiddleware(model="gpt-4o-mini", trigger=("messages", 6)),
        # ... kolejne middleware
    ],
)
```

To wszystko — reszta kodu agenta wygląda identycznie jak w lab-05.

---

## 4. SummarizationMiddleware — streszczanie historii

**Problem:** w długiej rozmowie historia rośnie i w końcu przekracza okno
kontekstu modelu (a każdy token kosztuje).

**Rozwiązanie:** gdy historia urośnie do progu (`trigger`), middleware streszcza
starsze wiadomości jednym podsumowaniem, **zachowując** kilka najnowszych
(`keep`).

```python
from langchain.agents.middleware import SummarizationMiddleware

SummarizationMiddleware(
    model="gpt-4o-mini",
    trigger=("messages", 6),   # streść, gdy w historii pojawi się 6 wiadomości
    keep=("messages", 2),      # zostaw 2 ostatnie w oryginale
)
```

Progi można wyrażać też w tokenach lub jako ułamek okna kontekstu:

- `trigger=("tokens", 4000)` — streść po przekroczeniu 4000 tokenów,
- `trigger=("fraction", 0.8)` — streść po zapełnieniu 80% okna kontekstu.

> Wymaga `checkpointer` (np. `InMemorySaver`), bo operuje na stanie wątku.

Pełny przykład: [solution/01_summarization.py](solution/01_summarization.py).

---

## 5. PIIMiddleware — ochrona danych wrażliwych

**Problem:** użytkownik wkleja e-mail, numer karty czy adres IP. Nie chcemy, by
takie dane trafiły do modelu albo do logów.

**Rozwiązanie:** middleware wykrywa PII i stosuje wybraną **strategię**:

| Strategia | Działanie | Przykład `jan@x.pl` |
|-----------|-----------|---------------------|
| `redact` | zastępuje etykietą | `[REDACTED_EMAIL]` |
| `mask` | maskuje część znaków | `j••@x.pl` |
| `hash` | zastępuje skrótem | `a1b2c3...` |
| `block` | blokuje całą wiadomość (wyjątek) | — |

```python
from langchain.agents.middleware import PIIMiddleware

middleware=[
    PIIMiddleware("email", strategy="redact", apply_to_input=True),
    PIIMiddleware("credit_card", strategy="mask", apply_to_input=True),
    PIIMiddleware("ip", strategy="hash", apply_to_input=True),
]
```

Wbudowane typy PII: `email`, `credit_card`, `ip`, `mac_address`, `url`. Można
też zdefiniować **własny detektor** — jako wzorzec regex albo funkcję.

```python
PIIMiddleware("api_key", detector=r"sk-[a-zA-Z0-9]{32}", strategy="block")
```

Pełny przykład: [solution/02_pii_detection.py](solution/02_pii_detection.py).

---

## 6. Limity wywołań — Model/Tool call limit

**Problem:** błędnie rozumujący agent może wpaść w pętlę i wykonać dziesiątki
płatnych wywołań modelu lub narzędzi.

**Rozwiązanie:** twarde limity. Po przekroczeniu agent kończy bieg
(`exit_behavior="end"`) lub rzuca wyjątek (`"error"`).

```python
from langchain.agents.middleware import (
    ModelCallLimitMiddleware,
    ToolCallLimitMiddleware,
)

middleware=[
    # Limit wywołań MODELU
    ModelCallLimitMiddleware(thread_limit=4, run_limit=4, exit_behavior="end"),
    # Limit wywołań konkretnego NARZĘDZIA
    ToolCallLimitMiddleware(tool_name="calculator", run_limit=2, exit_behavior="end"),
]
```

Różnica `thread_limit` vs `run_limit`:

- `run_limit` — limit w pojedynczym wywołaniu `invoke` (jeden „bieg”),
- `thread_limit` — limit w całym wątku (sumarycznie przez wiele tur rozmowy).

> Uwaga (typowanie): te dwa middleware mają różne typy stanu. Łącząc je w jednej
> liście, otypuj ją bazową klasą: `list[AgentMiddleware[Any, Any, Any]]`.

Pełny przykład: [solution/03_call_limits.py](solution/03_call_limits.py).

---

## 7. HumanInTheLoopMiddleware — zgoda człowieka

**Problem:** akcje nieodwracalne (wysłanie e-maila, płatność, zapis do bazy)
nie powinny dziać się bez nadzoru.

**Rozwiązanie:** middleware **wstrzymuje** agenta tuż przed wywołaniem wskazanego
narzędzia (mechanizm *interrupt*) i czeka na decyzję: `approve`, `edit` lub
`reject`.

```python
from langchain.agents.middleware import HumanInTheLoopMiddleware

HumanInTheLoopMiddleware(
    interrupt_on={
        "send_email": {"allowed_decisions": ["approve", "edit", "reject"]},
        "read_email": False,   # bezpieczne — bez przerywania
    }
)
```

Po przerwaniu wynik `invoke` zawiera klucz `__interrupt__`. Bieg wznawiasz,
przekazując decyzję przez `Command(resume=...)`:

```python
from langgraph.types import Command

result = agent.invoke({"messages": [...]}, config)

while "__interrupt__" in result:
    # ...pokaż operatorowi szczegóły akcji i zbierz decyzję...
    decision = {"type": "approve"}          # albo {"type": "reject", "message": "..."}
    result = agent.invoke(
        Command(resume={"decisions": [decision]}),
        config,
    )
```

> Wymaga `checkpointer` — stan jest zapamiętywany na czas przerwy. `config`
> musi zawierać ten sam `thread_id` przy pierwszym wywołaniu i przy wznowieniu.

Pełny przykład: [solution/04_human_in_the_loop.py](solution/04_human_in_the_loop.py).

---

## 8. ToolRetryMiddleware — automatyczne ponowienia

**Problem:** zewnętrzne API bywają zawodne — chwilowy błąd sieci nie powinien
wywracać całego zadania.

**Rozwiązanie:** middleware ponawia nieudane wywołanie narzędzia z **rosnącym
odstępem** (exponential backoff).

```python
from langchain.agents.middleware import ToolRetryMiddleware

ToolRetryMiddleware(
    max_retries=3,        # do 3 ponowień po pierwszej nieudanej próbie
    initial_delay=0.5,    # pierwszy odstęp: 0.5 s
    backoff_factor=2.0,   # kolejne: 0.5 s → 1 s → 2 s ...
    jitter=False,         # bez losowości (przewidywalne demo)
)
```

W przykładzie narzędzie `unstable_api` zawodzi 2 pierwsze razy, a za trzecim
zwraca wynik — agent kończy sukcesem dzięki ponowieniom.

> Pokrewne middleware: `ModelRetryMiddleware` robi to samo dla wywołań **modelu**.

Pełny przykład: [solution/05_tool_retry.py](solution/05_tool_retry.py).

---

## 9. Łączenie middleware

Middleware to klocki — można je składać w jednej liście. **Kolejność ma
znaczenie**: middleware otaczają wywołanie modelu jak warstwy cebuli — pierwsze
na liście jest „najbardziej zewnętrzne”.

```python
middleware = [
    PIIMiddleware("email", strategy="redact", apply_to_input=True),
    SummarizationMiddleware(model="gpt-4o-mini", trigger=("messages", 8), keep=("messages", 3)),
    ModelCallLimitMiddleware(thread_limit=8, run_limit=6, exit_behavior="end"),
    ToolRetryMiddleware(max_retries=3, initial_delay=0.5, jitter=False),
]
```

Taki agent jednocześnie: sanityzuje dane wrażliwe, streszcza długą historię,
pilnuje budżetu wywołań i ponawia zawodne narzędzia.

Pełny przykład: [solution/06_combined.py](solution/06_combined.py).

---

## 10. Inne wbudowane middleware (do samodzielnego poznania)

LangChain dostarcza więcej gotowych middleware — warto je znać:

| Middleware | Zastosowanie |
|------------|--------------|
| `ModelFallbackMiddleware` | przełączenie na zapasowy model, gdy główny zawiedzie |
| `LLMToolSelectorMiddleware` | wstępny wybór najistotniejszych narzędzi (gdy jest ich wiele) |
| `LLMToolEmulator` | emulacja narzędzi przez LLM (testy bez realnych wywołań) |
| `TodoListMiddleware` | planowanie zadań — dodaje narzędzie `write_todos` |
| `ContextEditingMiddleware` | czyszczenie starych wyników narzędzi z kontekstu |
| `ModelRetryMiddleware` | ponowienia wywołań modelu |

Pełna lista i opcje: [Prebuilt middleware](https://docs.langchain.com/oss/python/langchain/middleware/built-in).

---

## 11. Dobre praktyki

- **jedna troska = jedno middleware** — łatwiej testować i wymieniać,
- **limity zawsze na produkcji** — `ModelCallLimitMiddleware` chroni budżet,
- **PII jak najwcześniej** (`apply_to_input=True`) — model nie powinien widzieć surowych danych,
- **human-in-the-loop dla akcji nieodwracalnych** — wysyłka, płatność, zapis,
- **retry tylko dla błędów przejściowych** — nie maskuj nimi błędów logiki,
- pamiętaj o **`checkpointer`** tam, gdzie middleware operuje na stanie wątku
  (streszczanie, limity wątkowe, human-in-the-loop).

---

## 12. Najczęstsze błędy

- brak `checkpointer` przy `SummarizationMiddleware` / `HumanInTheLoopMiddleware`,
- inny (lub brakujący) `thread_id` przy wznawianiu po przerwie HITL,
- łączenie middleware o różnych typach stanu bez otypowania listy jako
  `list[AgentMiddleware[Any, Any, Any]]` (błąd typowania, nie działania),
- zbyt agresywny retry dla błędów, które nie są przejściowe,
- strategia PII `block` tam, gdzie wystarczyłoby `redact` — niepotrzebne wyjątki.

---

## 13. Co dalej?

- **własne middleware** — napisz klasę z zaczepami `before_model` / `after_model`,
- **PII na wyjściu i w wynikach narzędzi** — `apply_to_output`, `apply_to_tool_results`,
- **fallback + retry** — zbuduj naprawdę odpornego agenta produkcyjnego,
- **human-in-the-loop w UI/API** — opakuj przerwania w Streamlit (lab-03) lub FastAPI (lab-02),
- **pamięć i RAG** — połącz middleware z agentem z pamięcią z lab-05 i retrieverem z lab-04.

Gotowe implementacje znajdziesz w katalogu [solution/](solution/).
