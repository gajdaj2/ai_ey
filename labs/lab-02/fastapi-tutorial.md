# FastAPI — Wprowadzenie

## Czym jest FastAPI?

`FastAPI` to nowoczesny framework do budowania API HTTP w Pythonie. Łączy on:

- **szybkość** — jedna z najszybszych aplikacji webowych w Pythonie,
- **prostotę** — minimalna ilość kodu, maksimum funkcjonalności,
- **automatyczną dokumentację** — Swagger (`/docs`) generuje się z kodu,
- **type hints** — pełne wsparcie dla type annotations z Pythona 3.6+,
- **walidację danych** — integracja z `Pydantic`.

---

## Po co FastAPI?

### Alternatywy i porównanie

| Framework | Złożoność | Szybkość | Dokumentacja | Use case |
|-----------|-----------|----------|--------------|----------|
| **Flask** | niska | średnia | manualna | małe aplikacje, prototypy |
| **FastAPI** | niska | wysoka | automatyczna | API, microservices, MVP |
| **Django** | wysoka | średnia | automatyczna | duże aplikacje, full-stack |

**FastAPI jest idealnym wyborem dla:**
- szybkich prototypów API,
- microservices,
- integracji z modelami LLM,
- aplikacji, które muszą być skalowalne od razu.

---

## Instalacja

### 1. Uaktywnianie środowiska wirtualnego

```bash
# Jeśli jeszcze nie masz venv
python -m venv .venv

# Uaktywnienie (macOS / Linux)
source .venv/bin/activate

# Uaktywnienie (Windows)
.venv\Scripts\activate
```

### 2. Instalacja FastAPI i serwera

```bash
pip install fastapi uvicorn
```

Lub z plikiem `requirements.txt`:

```bash
pip install -r requirements.txt
```

---

## Pierwszy serwer

### Minimalny kod

Utwórz plik `hello.py`:

```python
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def root():
    return {"message": "Hello, FastAPI!"}


@app.get("/items/{item_id}")
def read_item(item_id: int):
    return {"item_id": item_id}
```

### Uruchomienie

```bash
uvicorn hello:app --reload
```

Flagi:
- `hello:app` — moduł `hello`, zmienna `app`,
- `--reload` — automatyczne przeładowanie przy zmianach kodu.

### Testowanie

Otwórz przeglądarke:

- `http://127.0.0.1:8000/` — root endpoint,
- `http://127.0.0.1:8000/items/42` — endpoint z parametrem,
- `http://127.0.0.1:8000/docs` — automatyczna dokumentacja Swagger,
- `http://127.0.0.1:8000/redoc` — alternatywna dokumentacja ReDoc.

---

## HTTP metody

FastAPI wspiera wszystkie standardowe metody HTTP:

```python
@app.get("/items")
def list_items():
    """Pobierz listę wszystkich elementów"""
    return [{"id": 1, "name": "Item 1"}]


@app.post("/items")
def create_item(name: str):
    """Utwórz nowy element"""
    return {"id": 2, "name": name}


@app.put("/items/{item_id}")
def update_item(item_id: int, name: str):
    """Zaktualizuj element"""
    return {"id": item_id, "name": name}


@app.delete("/items/{item_id}")
def delete_item(item_id: int):
    """Usuń element"""
    return {"deleted": True, "id": item_id}
```

---

## Parametry — Query, Path, Body

### Path Parameters (w adresie URL)

```python
@app.get("/users/{user_id}")
def get_user(user_id: int):
    return {"user_id": user_id}
```

Wywołanie: `GET /users/123`

### Query Parameters (po `?`)

```python
@app.get("/search")
def search(q: str, skip: int = 0, limit: int = 10):
    return {"query": q, "skip": skip, "limit": limit}
```

Wywołanie: `GET /search?q=python&skip=5&limit=20`

### Body Parameters (JSON w treści żądania)

```python
from pydantic import BaseModel


class Item(BaseModel):
    name: str
    description: str = None
    price: float


@app.post("/items")
def create_item(item: Item):
    return {"created": item}
```

Przykład żądania:

```bash
curl -X POST http://127.0.0.1:8000/items \
  -H "Content-Type: application/json" \
  -d '{"name": "Laptop", "price": 1000}'
```

---

## Modele Pydantic — walidacja danych

`Pydantic` automatycznie waliduje typy danych i generuje błędy, jeśli dane są niepoprawne.

```python
from pydantic import BaseModel, Field


class User(BaseModel):
    id: int
    name: str
    email: str
    age: int = Field(ge=0, le=120)  # age między 0 a 120


@app.post("/users")
def create_user(user: User):
    # user jest już walidowany
    return {"user": user}
```

### Walidacja w akcji

Żądanie poprawne:

```json
{
  "id": 1,
  "name": "Alice",
  "email": "alice@example.com",
  "age": 30
}
```

Żądanie niepoprawne (FastAPI automatycznie zwróci błąd):

```json
{
  "id": 1,
  "name": "Bob",
  "email": "not-an-email",
  "age": 150
}
```

Odpowiedź błędu:

```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "invalid email format",
      "type": "value_error.email"
    },
    {
      "loc": ["body", "age"],
      "msg": "ensure this value is less than or equal to 120",
      "type": "value_error.number.not_le"
    }
  ]
}
```

---

## Response Models

Możesz zdefiniować, jaki dokładnie model ma być zwracany:

```python
from pydantic import BaseModel


class Item(BaseModel):
    id: int
    name: str
    price: float


@app.get("/items/{item_id}", response_model=Item)
def get_item(item_id: int):
    # Zwracany obiekt musi pasować do Item
    return {"id": item_id, "name": "Laptop", "price": 999.99}
```

Dzięki `response_model`:
- FastAPI waliduje odpowiedź,
- Swagger dokumentuje dokładnie co endpoint zwraca,
- Można ukrywać pola wrażliwe (np. hasła).

---

## Status codes (kody HTTP)

Zwracianie różnych kodów statusu:

```python
from fastapi import status, HTTPException


@app.get("/items/{item_id}")
def get_item(item_id: int):
    if item_id < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID musi być większe od 0"
        )
    if item_id > 1000:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Element nie znaleziony"
        )
    return {"id": item_id, "name": "Laptop"}


@app.post("/items", status_code=status.HTTP_201_CREATED)
def create_item(item: dict):
    return {"created": item}
```

Powszechne kody:
- `200` — OK (sukces),
- `201` — Created (utworzono),
- `400` — Bad Request (błędne dane),
- `404` — Not Found (nie znaleziono),
- `500` — Internal Server Error (błąd serwera).

---

## Uruchamianie w produkcji

### Development (z `--reload`)

```bash
uvicorn app:app --reload
```

### Production (bez reload)

```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --workers 4
```

Parametry:
- `--host 0.0.0.0` — nasłuchuj na wszystkich interfejsach sieciowych,
- `--port 8000` — port,
- `--workers 4` — liczba procesów worker.

---

## Testowanie API

### Z Swaggera (w przeglądarce)

Otwórz `http://127.0.0.1:8000/docs`, spróbuj endpointów bezpośrednio w UI.

### Z `curl`

```bash
# GET
curl http://127.0.0.1:8000/items/1

# POST
curl -X POST http://127.0.0.1:8000/items \
  -H "Content-Type: application/json" \
  -d '{"name": "New Item"}'

# PUT
curl -X PUT http://127.0.0.1:8000/items/1 \
  -H "Content-Type: application/json" \
  -d '{"name": "Updated Item"}'

# DELETE
curl -X DELETE http://127.0.0.1:8000/items/1
```

### Z Pythona (`requests`)

```python
import requests

response = requests.post(
    "http://127.0.0.1:8000/items",
    json={"name": "Laptop", "price": 1000}
)
print(response.json())
```

---

## Dobre praktyki

### 1. Strukturuj projekt

```
my_api/
├── app.py           # główna aplikacja
├── models.py        # modele Pydantic
├── routes.py        # endpointy
├── database.py      # połączenie z bazą
└── config.py        # konfiguracja
```

### 2. Używaj docstringów

```python
@app.get("/items/{item_id}")
def get_item(item_id: int):
    """
    Pobierz element po ID.
    
    - **item_id**: unikalny identyfikator elementu
    
    Zwraca element o podanym ID.
    """
    return {"id": item_id}
```

Docstring pojawi się w dokumentacji Swaggera!

### 3. Waliduj dane wejściowe

Zawsze używaj modeli `Pydantic`:

```python
# ❌ Zły kod
@app.post("/items")
def create(name: str):
    return {"name": name}

# ✅ Dobry kod
class Item(BaseModel):
    name: str
    description: str = None

@app.post("/items")
def create(item: Item):
    return {"created": item}
```

### 4. Obsługuj błędy

```python
from fastapi import HTTPException

@app.get("/items/{item_id}")
def get_item(item_id: int):
    if item_id < 1:
        raise HTTPException(
            status_code=400,
            detail="ID nie może być ujemne"
        )
    return {"id": item_id}
```

### 5. Dokumentuj endpointy

```python
@app.get(
    "/items/{item_id}",
    summary="Pobierz element",
    description="Zwraca element o podanym identyfikatorze",
    response_description="Dane elementu"
)
def get_item(item_id: int):
    return {"id": item_id}
```

---

## Integracja z LangChain

FastAPI idealnie pasuje do `LangChain`:

```python
from fastapi import FastAPI
from pydantic import BaseModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser


class LessonRequest(BaseModel):
    topic: str
    audience: str = "junior developer"


class LessonResponse(BaseModel):
    topic: str
    lesson: str


app = FastAPI()

# Przygotuj chain
prompt = ChatPromptTemplate.from_messages([
    ("system", "Jesteś ekspertem edukacji technicznej."),
    ("human", "Przygotuj lekcję o {topic} dla {audience}"),
])
model = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)
chain = prompt | model | StrOutputParser()


@app.post("/lesson", response_model=LessonResponse)
def generate_lesson(request: LessonRequest):
    lesson = chain.invoke({
        "topic": request.topic,
        "audience": request.audience,
    })
    return LessonResponse(topic=request.topic, lesson=lesson)
```

---

## Co dalej?

Po tym wprowadzeniu możesz:

- dodać obsługę bazy danych (SQLAlchemy, Tortoise ORM),
- zaimplementować autentykację (JWT, OAuth2),
- dodać streaming odpowiedzi,
- skonfigurować CORS dla frontendów,
- deployować na Heroku, Railway, AWS Lambda.

Dla głębszej nauki: https://fastapi.tiangolo.com/

---

## Podsumowanie

`FastAPI` to prosty i potężny framework do budowania API:

✅ Naprawdę szybki w kodowaniu  
✅ Automatyczna dokumentacja  
✅ Silna walidacja danych  
✅ Świetny dla integracji z LangChain  
✅ Łatwy do skalowania  

Start znaj znajdziesz w `lab-02/tutorial.md` — tam pokazujemy pełny przykład integracji FastAPI z LangChain i OpenAI.
