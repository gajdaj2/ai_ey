# Lab 01b — Ćwiczenia

Po przeczytaniu `tutorial.md` wykonaj poniższe ćwiczenia. Każde ćwiczenie powinno być zapisane w osobnym pliku `.py`.

> **Warunki**: Ollama uruchomiona (`ollama serve`), co najmniej jeden model pobrany (`ollama pull llama2`).

---

## Ćwiczenie 1: Podstawowe zapytanie

**Cel:** Przyzwyczaić się do podstawowej składni Ollama + LangChain.

**Zadanie:**

Utwórz plik `cwiczenie_1_basic.py` i wykonaj 3 zapytania do modelu:

```python
# TODO: 
# 1. Zaimportuj Ollama z langchain_community
# 2. Utwórz instancję z modelem "llama2"
# 3. Wykonaj zapytanie: "Czym jest machine learning?"
# 4. Wyświetl odpowiedź
# 5. Wykonaj zapytanie: "Wymień 3 języki programowania"
# 6. Wykonaj zapytanie: "Czym się zajmujesz?" (sprawdź, jak model się przedstawi)
```

**Oczekiwany output:**
```
Odpowiedź 1: Machine learning to dziedzina...
Odpowiedź 2: 1. Python 2. Java 3. C++
Odpowiedź 3: Jestem asystentem AI...
```

**Wskazówka:** Patrz `tutorial.md` sekcja 2.

---

## Ćwiczenie 2: Parametry modelu

**Cel:** Zrozumieć wpływ parametrów na odpowiedzi.

**Zadanie:**

Utwórz plik `cwiczenie_2_parametry.py`. Dla tego samego zapytania uruchom model z różnymi parametrami:

```python
# Zapytanie: "Opisz ideę funkcjonalnego programowania"
# Uruchom model 3x z różnymi temperaturami:
#   - temperature=0.1 (deterministyczne)
#   - temperature=0.7 (średnie)
#   - temperature=1.5 (twórcze)

# Następnie dla temperature=0.7 spróbuj różnych top_k:
#   - top_k=5
#   - top_k=40
#   - top_k=100
```

**Pytania do refleksji:**
- Jak zmienia się odpowiedź w zależności od parametrów?
- Czy przy niskiej temperature odpowiedzi są zawsze takie same?
- Co się dzieje z top_k = 5?

**Wskazówka:** Patrz `tutorial.md` sekcja 3.

---

## Ćwiczenie 3: Łańcuchy LCEL

**Cel:** Zbudować łańcuch prompt → model → parser.

**Zadanie:**

Utwórz plik `cwiczenie_3_lanczuchy.py`:

```python
# Zaimportuj: ChatPromptTemplate, StrOutputParser, Ollama
# Utwórz prompt: "Wyjaśnij {koncepcja} w prostych słowach (max 30 słów)"
# Zbuduj łańcuch: prompt | llm | parser
# Uruchom dla:
#   - "Python"
#   - "API"
#   - "Bazy danych"
# Wyświetl wszystkie odpowiedzi
```

**Oczekiwany output:**
```
Koncepcja: Python
Odpowiedź: Python to język programowania...

Koncepcja: API
Odpowiedź: API to interfejs...
```

**Bonus:** Dodaj logowanie czasu wykonania każdego zapytania.

**Wskazówka:** Patrz `tutorial.md` sekcja 5.

---

## Ćwiczenie 4: Porównanie modeli

**Cel:** Zrozumieć różnice między modelami dostępnymi w Ollamie.

**Zadanie:**

Pobierz drugi model:
```bash
ollama pull neural-chat
```

Utwórz plik `cwiczenie_4_modele.py`:

```python
# Zdefiniuj to samo zapytanie: "Opisz rolę DevOps inżyniera"
# Uruchom zapytanie dla dwóch modeli:
#   1. llama2
#   2. neural-chat
# Zmierz czas odpowiedzi dla każdego
# Wyświetl: [Model] | [Czas] | [Odpowiedź]

# Dodatkowe kolumny do porównania mogą być:
# - Długość odpowiedzi (liczba znaków/słów)
# - Jakość (subjektywna ocena 1-5)
```

**Tabela do wypełnienia:**
| Model | Czas (s) | Długość | Jakość | Uwagi |
|-------|----------|--------|--------|-------|
| llama2 | ? | ? | ? | ? |
| neural-chat | ? | ? | ? | ? |

**Wskazówka:** Użyj `time.time()` do pomiaru czasu.

---

## Ćwiczenie 5: Strukturyzowany output

**Cel:** Użyć PydanticOutputParser do strukturyzowanych danych.

**Zadanie:**

Utwórz plik `cwiczenie_5_struktura.py`:

```python
# Definiuj model Pydantic dla "Autor":
#   - imie: str
#   - nazwisko: str
#   - najslynniejsza_ksiazka: str
#   - rok_urodzenia: int

# Utwórz prompt: "Opisz autora {nazwa}"
# Zdefiniuj PydanticOutputParser
# Uruchom łańcuch dla:
#   - "J.K. Rowling"
#   - "George R.R. Martin"

# Wyświetl strukturyzowane dane:
# Imię: ...
# Nazwisko: ...
# itd.
```

**Oczekiwany output:**
```
Autor: J.K. Rowling
  Imię: Joanne
  Nazwisko: Rowling
  Najsłynniejsza książka: Harry Potter i Kamień Filozoficzny
  Rok urodzenia: 1965
```

**Wskazówka:** Patrz `tutorial.md` sekcja 5 (drugi przykład).

---

## Ćwiczenie 6: Streaming (Bonus)

**Cel:** Wyświetlać odpowiedź na bieżąco bez czekania.

**Zadanie:**

Utwórz plik `cwiczenie_6_streaming.py`:

```python
# Utwórz funkcję callback, która wyświetla tokeny na bieżąco
# Uruchom model z "Napisz bajkę o lisie (5 zdań)" z callbackiem
# Powinna być widoczna progresywna odpowiedź

# Bonus: Dodaj animację (print ".") co drugi token
```

**Oczekiwany output:**
```
Streaming odpowiedź:
Dawno, dawno temu żył sobie . lis . który był znany z . 
```

**Wskazówka:** Patrz `tutorial.md` sekcja 6.

---

## Ćwiczenie 7: Multi-turn conversation

**Cel:** Symulować konwersację wieloobrotową.

**Zadanie:**

Utwórz plik `cwiczenie_7_konwersacja.py`:

```python
# Symuluj konwersację (kilka obrotów):
# Użytkownik: "Cześć, jestem wyuczony w Pythonie"
# Bot: [odpowiedź]
# Użytkownik: "Chcę nauczyć się Django"
# Bot: [odpowiedź biorąca pod uwagę kontekst?]
# Użytkownik: "Co to jest ORM?"
# Bot: [odpowiedź]

# WAŻNE: Standardowy Ollama NIE MA pamięci konwersacji
# Dlatego musisz ręcznie budować kontekst:

# kontekst = ""
# dla każdego zapytania:
#   kontekst += f"Użytkownik: {zapytanie}\n"
#   odpowiedź = model.invoke(kontekst)
#   kontekst += f"Bot: {odpowiedź}\n"
```

**Bonus:** Zapisz konwersację do pliku JSON.

---

## Ćwiczenie 8: Porównanie Ollama vs. Lab-01 (Zaawansowane)

**Cel:** Porównać Ollama z OpenAI API z lab-01.

**Zadanie:**

Jeśli masz `OPENAI_API_KEY`, utwórz `cwiczenie_8_porownanie.py`:

```python
# To ćwiczenie wymaga:
# - Ollama z modelem
# - OpenAI API key

# Zdefiniuj to samo zapytanie: "Wyjaśnij debugowanie w kodzie"
# Uruchom dla:
#   1. Ollama (llama2)
#   2. OpenAI (gpt-4o-mini)

# Porównaj:
#   - Czas odpowiedzi
#   - Długość odpowiedzi
#   - Jakość odpowiedzi (1-5)
#   - Tabulacyjne podsumowanie

# Wnioski do wyciągnięcia:
# - Czy odpowiedzi się różnią?
# - Czy czas jest znacząco inny?
# - Kiedy użyć lokalnie, a kiedy API?
```

---

## Ćwiczenie 9: Integracja z FastAPI (Zaawansowane)

**Cel:** Uruchomić prosty endpoint API z Ollama.

**Zadanie:**

Utwórz plik `cwiczenie_9_fastapi.py`:

```python
from fastapi import FastAPI
from pydantic import BaseModel
from langchain_community.llms import Ollama

app = FastAPI()
llm = Ollama(model="llama2")

class QueryRequest(BaseModel):
    question: str

@app.post("/ask")
async def ask_ollama(request: QueryRequest):
    response = llm.invoke(request.question)
    return {"question": request.question, "answer": response}

# Uruchom: uvicorn cwiczenie_9_fastapi:app --reload
# Testuj: curl -X POST http://localhost:8000/ask \
#   -H "Content-Type: application/json" \
#   -d '{"question": "Czym jest REST API?"}'
```

**Wskazówka:** Wymaga zainstalowania FastAPI i Uvicorn.

---

## Ćwiczenie 10: Własne eksperyment

**Cel:** Samodzielny projekt łączący wiedzę z tutoriala.

**Zadanie — wybierz jeden z poniższych:**

### Opcja A: Q&A System
Utwórz system, który:
- Pobiera pytania z pliku JSON
- Generuje odpowiedzi Ollama
- Zapisuje wyniki do CSV
- Oblicza średni czas odpowiedzi

### Opcja B: Prompt Engineering
Przetestuj wpływ różnych promptów na jakość:
```python
prompts = [
    "Wyjaśnij {temat}",
    "Jesteś ekspertem. Wyjaśnij {temat}",
    "Wyjaśnij {temat} jak dla 10-latka",
]
# Dla każdego promptu: uruchom, zmierz, porównaj
```

### Opcja C: Batch Processing
Utwórz skrypt, który:
- Przetwarza listę pytań w batch
- Pokazuje progres
- Loguje czasy odpowiedzi
- Generuje raport

**Plik:** `cwiczenie_10_projekt.py`

---

## Podsumowanie

Po wykonaniu ćwiczeń powinieneś umieć:
- ✅ Uruchamiać Ollama i podłączać do LangChain
- ✅ Konfigurować parametry modelu
- ✅ Budować łańcuchy LCEL
- ✅ Porównywać modele i API
- ✅ Integrować z FastAPI
- ✅ Eksperymentować z prompt engineeringiem

---

## Podpowiedzi do debugowania

| Problem | Rozwiązanie |
|---------|------------|
| ImportError: `langchain_community` | `pip install langchain-community` |
| "Connection refused" | Sprawdź `ollama serve` w innym terminalu |
| Timeout | Zwiększ `num_predict` lub zmień model |
| Odpowiedź nie ma struktury | Sprawdzaj format w `PydanticOutputParser` |

---

**Gotów? Zacznij od ćwiczenia 1! 🚀**
