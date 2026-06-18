# Inżynieria Aplikacji AI i Agentów LLM — repozytorium warsztatowe

Materiały do dwudniowych warsztatów hands-on. Repozytorium zawiera cztery laby — od prompt engineeringu po produkcyjnego agenta w LangGraph. Każdy lab ma kod startowy (`start.py`), gotowe rozwiązanie (`solution.py`) oraz własne README z instrukcją krok po kroku.

> Prowadzący: **Jakub Gajda** — AI Development Team Lead · Politechnika Gdańska
> Kontakt: kubus.pospolitos@gmail.com · linkedin.com/in/jakub-g-5823b54/

---

## Zawartość

| Lab | Temat | Czas | Katalog |
|-----|-------|------|---------|
| 1 | Prompt engineering — ekstrakcja danych do JSON ze schematem | ~30–40 min | `labs/01-prompt-engineering/` |
| 2 | Function calling — mini-agent z narzędziami w czystym SDK | ~35–45 min | `labs/02-function-calling/` |
| 3 | RAG — Q&A nad dokumentami z cytowaniem źródeł | ~45–55 min | `labs/03-rag/` |
| 4 | Agenci w LangGraph — pamięć, narzędzia, human-in-the-loop | ~55–70 min | `labs/04-agents-langgraph/` |

Laby są ułożone w kolejności rosnącej złożoności i częściowo na sobie bazują (narzędzia z labu 2 oraz retriever z labu 3 wracają w labie 4).

---

## Szybki start

### 1. Środowisko (zalecane: `uv`)

```bash
# instalacja uv (jeśli nie masz): https://docs.astral.sh/uv/
uv venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
uv pip install -r requirements.txt
```

Alternatywnie klasycznie:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Klucze API

Skopiuj `.env.example` do `.env` i uzupełnij swoje klucze:

```bash
cp .env.example .env
# edytuj .env i wpisz OPENAI_API_KEY=...
```

**Nigdy nie commituj pliku `.env`** — jest w `.gitignore`.

### 3. Uruchamianie labu

```bash
cd labs/01-prompt-engineering
python start.py        # Twoja wersja do uzupełnienia
python solution.py     # gotowe rozwiązanie referencyjne
```

---

## Wymagania

- Python 3.10+
- Klucz API do dostawcy LLM (domyślnie OpenAI; kod łatwo przełączyć na Anthropic)
- ~1 GB miejsca na modele embeddingów i bazę wektorową (lab 3 i 4)

## Wskazówki

- Każdy lab można robić niezależnie — `solution.py` jest samowystarczalne.
- Jeśli nie masz klucza OpenAI, w komentarzach każdego labu jest wariant na model lokalny / Anthropic.
- Utknąłeś? Najpierw zajrzyj do README danego labu, potem do `solution.py`.

Powodzenia w budowaniu! 🚀
