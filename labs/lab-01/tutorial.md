# Lab 01 — Podstawy LangChain z OpenAI

## Cel labu

W tym labie poznasz absolutne podstawy pracy z biblioteką **LangChain** i modelem **OpenAI** w Pythonie. Po wykonaniu tutorialu uczestnik powinien umieć:

- skonfigurować połączenie z modelem OpenAI,
- wykonać pojedyncze zapytanie przez `ChatOpenAI`,
- zbudować prompt z użyciem `ChatPromptTemplate`,
- połączyć kroki w prosty łańcuch LCEL (`prompt | model | parser`),
- wymusić bardziej uporządkowaną odpowiedź modelu.

---

## Wymagania

- Python 3.10+
- aktywne środowisko wirtualne,
- ustawiony klucz `OPENAI_API_KEY`,
- zainstalowane pakiety z `requirements.txt`.

Jeżeli środowisko nie jest jeszcze gotowe, użyj:

```bash
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

Albo klasycznie:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Ustaw klucz API:

```bash
export OPENAI_API_KEY="twoj_klucz"
```

---

## 1. Pierwsze wywołanie modelu

LangChain daje wygodną warstwę nad modelami LLM. Na start potrzebujemy tylko obiektu `ChatOpenAI`.

```python
from langchain_openai import ChatOpenAI

model = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.2,
)

response = model.invoke("Wyjaśnij w 3 zdaniach, czym jest LangChain.")
print(response.content)
```

### Co tu się dzieje?

- `ChatOpenAI` tworzy klienta modelu czatowego,
- `model` wskazuje konkretny model OpenAI,
- `temperature` kontroluje kreatywność odpowiedzi,
- `invoke(...)` wykonuje pojedyncze wywołanie.

---

## 2. Praca z wiadomościami

Modele czatowe dobrze działają, gdy jawnie rozdzielamy rolę systemu i użytkownika.

```python
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI

model = ChatOpenAI(model="gpt-4o-mini", temperature=0)

messages = [
    SystemMessage(content="Jesteś pomocnym asystentem dla początkujących programistów AI."),
    HumanMessage(content="Podaj 3 zastosowania LLM w firmie szkoleniowej."),
]

response = model.invoke(messages)
print(response.content)
```

To podejście jest przydatne, gdy chcesz:

- narzucić styl odpowiedzi,
- przekazać reguły bezpieczeństwa lub formatowania,
- odróżnić instrukcję od treści użytkownika.

---

## 3. Szablony promptów z `ChatPromptTemplate`

Zamiast ręcznie składać stringi, lepiej używać szablonów promptów.

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

prompt = ChatPromptTemplate.from_messages([
    ("system", "Jesteś ekspertem od edukacji technicznej."),
    ("human", "Przygotuj krótkie wyjaśnienie pojęcia: {topic}"),
])

model = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)

messages = prompt.invoke({"topic": "LangChain Expression Language"})
response = model.invoke(messages)

print(response.content)
```

### Dlaczego to ważne?

- prompt staje się wielokrotnego użytku,
- zmienne wejściowe są jawne,
- łatwiej testować różne warianty instrukcji.

---

## 3.1 Metody tworzenia szablonów: `from_template()` i `from_messages()`

`ChatPromptTemplate` oferuje dwie główne metody tworzenia szablonów. Warto znać obie, bo służą do różnych celów.

### `from_template()` — szybka i prosta

Gdy chcesz prostą instrukcję z kilkoma zmiennymi:

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

prompt = ChatPromptTemplate.from_template(
    "Wyjaśnij {concept} w kontekście {context}. Bądź zwięzły."
)

model = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)

messages = prompt.invoke({
    "concept": "API REST",
    "context": "szkolenie dla junior developerów"
})

response = model.invoke(messages)
print(response.content)
```

**Zalety:**
- bardzo krótko się pisze,
- idealna do jednoliniowych czy dwuliniowych promptów,
- zmienne wstawiasz jako `{placeholder}`.

**Ograniczenia:**
- cała treść trafia jako rola `human` (użytkownika),
- brak jawnej separacji systemu i użytkownika.

### `from_messages()` — pełna kontrola

Gdy potrzebujesz niezależnych ról systemu, asystenta czy użytkownika:

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

prompt = ChatPromptTemplate.from_messages([
    ("system", "Jesteś mentorem programowania. Zawsze podawaj konkretne przykłady kodu."),
    ("human", "Wyjaśnij mi {concept} w kategorii {difficulty}. Podaj mały example."),
])

model = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)

messages = prompt.invoke({
    "concept": "lambda funkcje",
    "difficulty": "zaawansowane"
})

response = model.invoke(messages)
print(response.content)
```

**Zalety:**
- pełna kontrola nad rolą każdej wiadomości,
- możesz dodać wiele ról (`system`, `human`, `ai`),
- łatwiej jest konstruować złożone instrukcje.

### Porównanie side-by-side

```python
# from_template() — jednolinijkowa, tylko human
prompt_simple = ChatPromptTemplate.from_template(
    "Opowiedz o {topic}"
)

# from_messages() — bardziej elastyczna
prompt_complex = ChatPromptTemplate.from_messages([
    ("system", "Jesteś ekspertem"),
    ("human", "Opowiedz o {topic}"),
])

# Oba działają z invoke(), ale strukturalnie się różnią
```

### Kiedy stosować co?

| Sytuacja | Metoda | Dlaczego |
|----------|--------|---------|
| Prosty prompt, 1 zmienna | `from_template()` | szybciej się pisze |
| Potrzebujesz system prompt | `from_messages()` | możesz ustawić rolę |
| Złożona instrukcja, wiele zmiennych | `from_messages()` | pełna kontrola |
| Prototyp, uczę się | `from_template()` | łatwiej początkować |
| Produkcja, precyzyjne zachowanie | `from_messages()` | jawna separacja ról |

---

## 4. Pierwszy łańcuch LCEL

W LangChain bardzo wygodnie buduje się przepływ danych przez operator `|`.

```python
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

prompt = ChatPromptTemplate.from_template(
    "Wypisz 3 praktyczne zastosowania technologii: {technology}. Odpowiadaj zwięźle."
)

model = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)
parser = StrOutputParser()

chain = prompt | model | parser

result = chain.invoke({"technology": "LangChain"})
print(result)
```

### Co daje `StrOutputParser`?

Domyślnie model zwraca obiekt wiadomości AI. Parser zamienia wynik na zwykły tekst, dzięki czemu dalsza praca jest prostsza.

---

## 5. Wymuszenie konkretnego formatu odpowiedzi

Jednym z najczęstszych zadań jest uzyskanie odpowiedzi w przewidywalnym formacie.

```python
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

prompt = ChatPromptTemplate.from_template(
    """
    Odpowiedz dokładnie w formacie:
    Tytuł: <jedna linia>
    Opis: <max 2 zdania>
    Poziom trudności: <niski/sredni/wysoki>

    Temat: {topic}
    """
)

chain = (
    prompt
    | ChatOpenAI(model="gpt-4o-mini", temperature=0)
    | StrOutputParser()
)

result = chain.invoke({"topic": "wprowadzenie do LangChain"})
print(result)
```

To jeszcze nie jest pełna walidacja struktury, ale już znacząco poprawia przewidywalność odpowiedzi.

### Wersja z walidacją przez `Pydantic`

Jeżeli chcesz **wymusić konkretną strukturę** i od razu dostać wynik jako obiekt Pydantic, użyj `PydanticOutputParser`.

```python
from pydantic import BaseModel, Field
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI


class LessonCard(BaseModel):
    tytul: str = Field(description="Krótki tytuł lekcji")
    opis: str = Field(description="Opis w maksymalnie 2 zdaniach")
    poziom: str = Field(description="Poziom trudności: niski/sredni/wysoki")


parser = PydanticOutputParser(pydantic_object=LessonCard)

prompt = ChatPromptTemplate.from_template(
    """
    Odpowiedz na temat: {topic}

    {format_instructions}
    """,
    partial_variables={"format_instructions": parser.get_format_instructions()},
)

chain = (
    prompt
    | ChatOpenAI(model="gpt-4o-mini", temperature=0)
    | parser
)

result = chain.invoke({"topic": "wprowadzenie do LangChain"})

print(type(result))         # <class '__main__.LessonCard'>
print(result.tytul)
print(result.opis)
print(result.poziom)
```

W tym podejściu:

- model dostaje jawne instrukcje formatu (`parser.get_format_instructions()`),
- odpowiedź jest parsowana do klasy `LessonCard`,
- od razu masz walidację typów i pól.

To jest pierwszy krok do stabilnych integracji API, gdzie frontend lub inny serwis oczekuje przewidywalnego JSON-a.

---

## 6. Mini-przykład: generator mikro-lekcji

Poniżej masz prosty przykład praktyczny do pokazania na zajęciach.

```python
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

prompt = ChatPromptTemplate.from_template(
    """
    Przygotuj mikro-lekcję dla junior developera.

    Temat: {topic}
    Długość: {length}

    Odpowiedź podziel na sekcje:
    1. Definicja
    2. Przykład
    3. Najczęstszy błąd
    """
)

chain = (
    prompt
    | ChatOpenAI(model="gpt-4o-mini", temperature=0.4)
    | StrOutputParser()
)

result = chain.invoke({
    "topic": "prompt template",
    "length": "krótka, maksymalnie 150 słów",
})

print(result)
```

---

## 7. Dobre praktyki na start

### Ustawiaj niską temperaturę, gdy chcesz przewidywalności

- `0` do `0.2` — dobre do ekstrakcji, klasyfikacji i instrukcji,
- `0.5+` — lepsze do kreatywnych treści.

### Rozdzielaj warstwy odpowiedzialności

Najprostszy sensowny układ to:

- `prompt` — buduje instrukcję,
- `model` — generuje odpowiedź,
- `parser` — porządkuje wynik.

### Testuj prompt na kilku wejściach

Prompt, który działa dla jednego przykładu, niekoniecznie działa dobrze dla innych. Warto sprawdzić kilka tematów, długości odpowiedzi i poziomów szczegółowości.

---

## 8. Najczęstsze błędy początkujących

- brak ustawionego `OPENAI_API_KEY`,
- używanie zbyt wysokiej temperatury przy zadaniach technicznych,
- ręczne składanie dużych promptów zamiast użycia templatek,
- brak parsera i późniejsze operowanie na obiekcie wiadomości zamiast na tekście,
- oczekiwanie idealnie sformatowanego outputu bez jawnej instrukcji formatu.

---

## 9. Co dalej?

Po tym labie uczestnik jest gotowy na kolejne kroki:

- structured output z `Pydantic`,
- korzystanie z narzędzi (`tools`),
- budowę prostych agentów,
- RAG i workflow wieloetapowy.

Jeśli chcesz, jako rozszerzenie do tego labu możesz dopisać własny plik `start.py` i przerobić przykłady na zadania wykonywane bezpośrednio w terminalu.
