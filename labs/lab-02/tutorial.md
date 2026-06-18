# Lab 02 — Tutorial: FastAPI z użyciem LangChain do OpenAI

## Cel labu

W tym labie zbudujesz prostą aplikację `FastAPI`, która udostępnia endpoint HTTP do generowania krótkiej mikro-lekcji z użyciem `LangChain` i modelu OpenAI.

Po wykonaniu labu uczestnik powinien umieć:

- utworzyć podstawową aplikację `FastAPI`,
- zdefiniować modele request/response w `Pydantic`,
- wywołać `ChatOpenAI` przez `LangChain`,
- złożyć prosty chain `prompt | model | parser`,
- wystawić to jako endpoint `POST`.

---

## Wymagania

- Python 3.10+
- aktywne środowisko wirtualne,
- ustawiony `OPENAI_API_KEY`,
- zainstalowane pakiety z głównego `requirements.txt`.

Uruchomienie środowiska:

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

Jeśli używasz `uv`:

```bash
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

Ustaw klucz API:

```bash
export OPENAI_API_KEY="twoj_klucz"
```

---

## 1. Po co łączyć FastAPI i LangChain?

`FastAPI` daje szybki sposób wystawienia API HTTP, a `LangChain` porządkuje pracę z modelami LLM.

Taki układ jest wygodny, gdy chcesz:

- udostępnić model jako usługę dla frontendów lub innych aplikacji,
- mieć walidację danych wejściowych,
- rozdzielić warstwę API od logiki promptów,
- łatwo rozwijać aplikację o kolejne endpointy.

---

## 2. Struktura przykładowej aplikacji

W tym labie gotowa aplikacja znajduje się w pliku:

- `solution/app.py`

Aplikacja będzie mieć dwa endpointy:

- `GET /health` — szybki test działania serwera,
- `POST /generate-lesson` — generowanie mikro-lekcji przez LLM.

---

## 3. Pierwsza aplikacja FastAPI

Minimalny serwer `FastAPI` wygląda tak:

```python
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "Hello API"}
```

Uruchomienie lokalnie:

```bash
uvicorn labs.lab-02.solution.app:app --reload
```

Po starcie możesz wejść na:

- `http://127.0.0.1:8000/docs`
- `http://127.0.0.1:8000/redoc`

To jedna z największych zalet `FastAPI`: dokumentacja API generuje się automatycznie.

---

## 4. Modele danych wejścia i wyjścia

W `FastAPI` bardzo wygodnie używa się modeli `Pydantic` do walidacji requestów i odpowiedzi.

Przykład:

```python
from pydantic import BaseModel


class GenerateLessonRequest(BaseModel):
    topic: str
    audience: str = "junior developer"
    max_words: int = 150


class GenerateLessonResponse(BaseModel):
    topic: str
    lesson: str
```

Dzięki temu:

- wejście jest walidowane automatycznie,
- Swagger pokazuje dokładny kontrakt API,
- łatwiej rozwijać endpointy w przewidywalny sposób.

---

## 5. Prosty chain w LangChain

Sercem rozwiązania jest prosty pipeline:

```python
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

prompt = ChatPromptTemplate.from_messages([
    ("system", "Jesteś ekspertem od edukacji technicznej."),
    ("human", "Przygotuj mikro-lekcję o temacie: {topic}"),
])

model = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)
parser = StrOutputParser()

chain = prompt | model | parser
```

Potem można wywołać:

```python
result = chain.invoke({"topic": "FastAPI"})
```

---

## 6. Wystawienie chaina jako endpoint `POST`

Teraz łączymy `FastAPI` i `LangChain`.

Przykładowy endpoint:

```python
@app.post("/generate-lesson", response_model=GenerateLessonResponse)
def generate_lesson(payload: GenerateLessonRequest) -> GenerateLessonResponse:
    lesson = chain.invoke(
        {
            "topic": payload.topic,
            "audience": payload.audience,
            "max_words": payload.max_words,
        }
    )
    return GenerateLessonResponse(topic=payload.topic, lesson=lesson)
```

Co się tutaj dzieje:

- `payload` jest automatycznie parsowany z JSON,
- `FastAPI` waliduje dane wejściowe,
- `LangChain` generuje odpowiedź,
- wynik wraca jako ustrukturyzowany JSON.

---

## 7. Pełny scenariusz biznesowy w tym labie

Endpoint przyjmuje dane wejściowe:

- `topic` — temat lekcji,
- `audience` — grupa odbiorców,
- `max_words` — maksymalna długość odpowiedzi.

Model ma wygenerować krótką mikro-lekcję z trzema sekcjami:

- definicja,
- przykład,
- najczęstszy błąd.

To dobry pierwszy use case, bo:

- jest prosty,
- pokazuje pełny przepływ request → LLM → response,
- łatwo go później rozszerzyć.

---

## 8. Testowanie endpointu

Po uruchomieniu serwera możesz użyć Swaggera albo `curl`.

### `curl`

```bash
curl -X POST http://127.0.0.1:8000/generate-lesson \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "LangChain",
    "audience": "junior python developer",
    "max_words": 120
  }'
```

### Przykładowa odpowiedź

```json
{
  "topic": "LangChain",
  "lesson": "1. Definicja: ...\n2. Przykład: ...\n3. Najczęstszy błąd: ..."
}
```

---

## 9. Obsługa błędów

W praktycznym API warto sprawdzić, czy `OPENAI_API_KEY` jest ustawiony. Jeśli nie, endpoint powinien zwrócić czytelny błąd.

Dobry pierwszy krok to:

- sprawdzenie klucza przy tworzeniu modelu,
- zwrócenie `HTTPException(status_code=500, detail=...)`.

Dzięki temu użytkownik API szybciej zrozumie problem.

---

## 10. Dobre praktyki

- trzymaj prompt w osobnej funkcji,
- waliduj request przez `Pydantic`,
- ustaw niską temperaturę dla odpowiedzi instruktażowych,
- dodaj prosty endpoint `health`,
- testuj endpoint zarówno przez `/docs`, jak i `curl`.

---

## 11. Co dalej?

Po tym labie naturalnym kolejnym krokiem są:

- structured output z `Pydantic`,
- streaming odpowiedzi,
- obsługa wielu endpointów z różnymi promptami,
- dodanie pamięci rozmowy lub RAG.

Gotową implementację znajdziesz w `solution/app.py`.
