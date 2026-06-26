# Lab 01b — Tutorial: LangChain + Ollama

> **Wymagania**: Ollama zainstalowana i uruchomiona (`ollama serve`), Python 3.10+, zainstalowane pakiety.

## Cel tutoriala

Po tym tutorialu będziesz umieć:
- Podłączyć LangChain do lokalnego modelu poprzez Ollama
- Wykonać zapytanie do lokalnego LLM
- Skonfigurować parametry modelu
- Zbudować prosty łańcuch LCEL z Ollama
- Porównać Ollama z OpenAI API

---

## 1. Czym jest Ollama?

**Ollama** to CLI narzędzie, które:
- Pobiera i zarządza modelami LLM
- Uruchamia serwer HTTP na porcie `11434`
- Pozwala na interakcję z modelami bez API

### Zainstaluj Ollama

Na https://ollama.ai dostępne wersje dla macOS, Linux i Windows (Preview).

Po instalacji, sprawdź:
```bash
ollama --version
```

### Pobierz model

```bash
# Najpopularniejsze modele:
ollama pull llama2           # Llama 2, uniwersalny
ollama pull mistral          # Mistral 7B, szybki
ollama pull neural-chat      # Neural Chat, dobrze dostrojony
```

Rozmiary to około 4–5 GB w zależności od modelu.

### Uruchom Ollama

W jednym terminalu:
```bash
ollama serve
```

Powinieneś zobaczyć:
```
Serving on http://0.0.0.0:11434
```

---

## 2. Pierwsze połączenie z LangChain

### Instalacja pakietów

```bash
pip install langchain langchain-community
```

### Prosty kod

Utwórz plik `test_ollama.py`:

```python
from langchain_community.llms import Ollama

# Utwórz instancję Ollama
llm = Ollama(model="llama2")

# Wykonaj zapytanie
response = llm.invoke("Czym jest Ollama w jednym zdaniu?")
print(response)
```

Uruchom:
```bash
python test_ollama.py
```

**Oczekiwana odpowiedź** (coś w tym stylu):
```
Ollama to lekkie narzędzie umożliwiające uruchamianie 
dużych modeli językowych lokalnie na komputerze 
bez konieczności używania zewnętrznych API.
```

---

## 3. Konfiguracja parametrów

Parametry modelu wpływają na wynik:

```python
from langchain_community.llms import Ollama

llm = Ollama(
    model="llama2",
    temperature=0.7,    # 0.0 = deterministyczne, 1.0 = chaotyczne
    top_k=40,           # Liczba najbardziej prawdopodobnych tokenów
    top_p=0.9,          # Nucleus sampling
)

response = llm.invoke("Wymyśl kreatywne nazwy dla kotów")
print(response)
```

### Parametry

| Parametr | Zakres | Opis |
|----------|--------|------|
| `temperature` | 0.0–2.0 | Wyższa = bardziej kreatywna |
| `top_k` | 1–100 | Ile top-N tokenów rozpatrywać |
| `top_p` | 0.0–1.0 | Nucleus sampling threshold |
| `repeat_penalty` | 1.0+ | Karanie za powtórzenia |

### Przykład: Mały model dla szybkości

```python
from langchain_community.llms import Ollama

llm = Ollama(
    model="neural-chat",  # Mniejszy model
    temperature=0.3,      # Bardziej deterministyczne
    num_predict=128,      # Max 128 tokenów
)

response = llm.invoke("Jaka jest stolica Polski?")
print(response)
```

---

## 4. Porównanie z OpenAI (lab-01)

### OpenAI w lab-01
```python
from langchain_openai import ChatOpenAI

model = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)
response = model.invoke("Czym jest LangChain?")
```

### Ollama (tu)
```python
from langchain_community.llms import Ollama

model = Ollama(model="llama2", temperature=0.2)
response = model.invoke("Czym jest LangChain?")
```

**Różnice:**
| Aspekt | OpenAI | Ollama |
|--------|--------|--------|
| Import | `langchain_openai` | `langchain_community` |
| Klasa | `ChatOpenAI` | `Ollama` |
| Wymaga API | Tak | Nie |
| Wymaga internetu | Tak | Nie (po pobraniu modelu) |
| Koszt | $ | Darmowe |

---

## 5. Łańcuchy LCEL z Ollama

Łańcuchy działają identycznie jak w lab-01, ale z Ollama:

### Prosty łańcuch

```python
from langchain_community.llms import Ollama
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Model
llm = Ollama(model="llama2", temperature=0.7)

# Prompt
prompt = ChatPromptTemplate.from_template(
    "Wyjaśnij {temat} jak dla dziecka (max 50 słów)."
)

# Parser
parser = StrOutputParser()

# Łańcuch LCEL
chain = prompt | llm | parser

# Użycie
result = chain.invoke({"temat": "sztuczna inteligencja"})
print(result)
```

### Łańcuch ze strukturyzowanym outputem

```python
from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field

# Definiuj strukturę
class Recipe(BaseModel):
    name: str = Field(description="Nazwa potrawy")
    ingredients: list[str] = Field(description="Składniki")
    time_minutes: int = Field(description="Czas przygotowania")

# Parser
parser = PydanticOutputParser(pydantic_object=Recipe)

# Prompt
prompt = PromptTemplate(
    template="""Zaproponuj przepis na {dish}.
{format_instructions}""",
    input_variables=["dish"],
    partial_variables={"format_instructions": parser.get_format_instructions()}
)

# Model
llm = Ollama(model="llama2", temperature=0.5)

# Łańcuch
chain = prompt | llm | parser

# Użycie
result = chain.invoke({"dish": "brownies"})
print(f"Danie: {result.name}")
print(f"Czas: {result.time_minutes} minut")
```

---

## 6. Streaming — Przyrostowy output

Ollama obsługuje streaming (wyświetlanie odpowiedzi na bieżąco):

```python
from langchain_community.llms import Ollama

llm = Ollama(model="llama2")

# Streaming callback
def print_stream(chunk):
    print(chunk, end="", flush=True)

# Invoke ze streaming
print("Streaming odpowiedź:\n")
llm.invoke("Opowiedz historię o kocie w 5 zdaniach.", callbacks=[print_stream])
```

---

## 7. Porady i Tricks

### Zmiana domyślnego portu

Jeśli port `11434` jest zajęty:

```bash
ollama serve --addr 0.0.0.0:8000
```

Wtedy w kodzie:
```python
llm = Ollama(model="llama2", base_url="http://localhost:8000")
```

### Limit odpowiedzi (num_predict)

```python
llm = Ollama(
    model="llama2",
    num_predict=50  # Max 50 tokenów
)
```

### Zwiększanie szybkości (GPU)

Jeśli masz GPU (CUDA, Metal), Ollama będzie używać. Sprawdź:
```bash
ollama show llama2 --modelfile
```

---

## 8. Troubleshooting

| Problem | Rozwiązanie |
|---------|------------|
| "Connection refused" | Uruchom `ollama serve` w innym terminalu |
| Model się zawieszył | Zmniejsz `temperature` lub `top_k` |
| Za wolno | Użyj `neural-chat` zamiast `llama2` |
| Brak pamięci RAM | Użyj `orca-mini` (2GB) |
| Model nie znaleziony | Uruchom `ollama pull [model_name]` |

---

## 9. Podsumowanie

**W tym tutorialu:**
- ✅ Zainstalowałeś Ollama
- ✅ Podłączyłeś LangChain do Ollama
- ✅ Nauczyłeś się konfigurować parametry
- ✅ Zbudowałeś łańcuchy LCEL
- ✅ Znasz różnice OpenAI vs Ollama

**Następnie:** Przejdź do `cwiczenia.md` i wykonaj praktyczne zadania!

---

**Szybka ściąga:**

```python
# Ollama + LangChain 30s setup
from langchain_community.llms import Ollama
from langchain.prompts import ChatPromptTemplate

llm = Ollama(model="llama2", temperature=0.7)
prompt = ChatPromptTemplate.from_template("Powiedz coś o {topic}")
chain = prompt | llm

result = chain.invoke({"topic": "Ollama"})
print(result)
```

Gotów na ćwiczenia? → Przejdź do `cwiczenia.md`! 🚀
