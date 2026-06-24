# Lab 01 — Python od zera (fundament przed LangChain)

## Cel materiału

Ten tutorial jest dla osób, które zaczynają od podstaw Pythona. Po przerobieniu materiału powinieneś/powinnaś umieć:

- pisać proste programy w Pythonie,
- używać instrukcji warunkowych, pętli i funkcji,
- pracować na listach, słownikach i plikach,
- rozumieć podstawy programowania obiektowego (OOP),
- przygotować się do dalszej części labu z LangChain.

---

## 0. Start: środowisko i uruchamianie

### Wymagania

- Python 3.10+
- aktywne środowisko wirtualne (`venv`)

### Szybki setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Pierwszy skrypt

Utwórz plik `hello.py`:

```python
print("Cześć! To mój pierwszy skrypt w Pythonie.")
```

Uruchom:

```bash
python hello.py
```

---

## 1. Podstawy składni

### Zmienne i typy

```python
name = "Ala"          # str
age = 28              # int
height = 1.68         # float
is_active = True      # bool
```

### Operatory

```python
x = 10
y = 3

print(x + y)   # 13
print(x - y)   # 7
print(x * y)   # 30
print(x / y)   # 3.333...
print(x % y)   # 1
```

### Tekst i f-string

```python
name = "Marek"
score = 92
print(f"Uczestnik: {name}, wynik: {score}%")
```

---

## 2. Sterowanie przepływem

### Warunki `if / elif / else`

```python
points = 78

if points >= 90:
    level = "A"
elif points >= 75:
    level = "B"
else:
    level = "C"

print(level)
```

### Pętle

```python
for i in range(1, 4):
    print(f"Iteracja {i}")

count = 0
while count < 3:
    print("while działa")
    count += 1
```

---

## 3. Struktury danych

### Lista (`list`)

```python
topics = ["Python", "LLM", "RAG"]
topics.append("LangChain")
print(topics)
```

### Słownik (`dict`)

```python
student = {
    "name": "Kasia",
    "score": 95,
}

print(student["name"])
student["score"] = 97
```

### Krotka (`tuple`) i zbiór (`set`)

```python
point = (10, 20)
unique_tags = {"ai", "python", "ai"}
print(point)
print(unique_tags)  # duplikaty są usunięte
```

### List comprehension

```python
numbers = [1, 2, 3, 4, 5]
squares = [n * n for n in numbers]
print(squares)
```

---

## 4. Funkcje

### Definiowanie funkcji

```python
def greet(name: str) -> str:
    return f"Cześć, {name}!"

print(greet("Ola"))
```

### Argumenty domyślne

```python
def power(base: int, exponent: int = 2) -> int:
    return base ** exponent

print(power(3))     # 9
print(power(3, 3))  # 27
```

### Dobre praktyki

- Funkcja powinna robić jedną rzecz.
- Dobrze nazywaj argumenty i zwracane wartości.
- Dodawaj proste adnotacje typów (`typing`).

---

## 5. Moduły i organizacja kodu

### Import modułu

```python
import math
print(math.sqrt(16))
```

### Import funkcji

```python
from math import sqrt
print(sqrt(25))
```

### Punkt wejścia programu

```python
def main():
    print("Uruchamiam aplikację")


if __name__ == "__main__":
    main()
```

---

## 6. Obsługa wyjątków

```python
def divide(a: float, b: float) -> float:
    try:
        return a / b
    except ZeroDivisionError:
        print("Nie dziel przez zero")
        return 0.0


print(divide(10, 2))
print(divide(10, 0))
```

Najczęściej spotkasz:

- `ValueError`
- `TypeError`
- `KeyError`
- `FileNotFoundError`

---

## 7. OOP — programowanie obiektowe

## 7.1 Klasa i obiekt

```python
class User:
    def __init__(self, name: str, role: str):
        self.name = name
        self.role = role

    def describe(self) -> str:
        return f"{self.name} ({self.role})"


u = User("Ania", "student")
print(u.describe())
```

## 7.2 Dziedziczenie

```python
class Person:
    def __init__(self, name: str):
        self.name = name

    def introduce(self) -> str:
        return f"Nazywam się {self.name}."


class Trainer(Person):
    def __init__(self, name: str, specialization: str):
        super().__init__(name)
        self.specialization = specialization

    def introduce(self) -> str:
        return f"Nazywam się {self.name}, specjalizacja: {self.specialization}."
```

## 7.3 Kompozycja

```python
class Address:
    def __init__(self, city: str):
        self.city = city


class Office:
    def __init__(self, name: str, address: Address):
        self.name = name
        self.address = address
```

## 7.4 `dataclass` (praktyczne uproszczenie)

```python
from dataclasses import dataclass


@dataclass
class Lesson:
    title: str
    duration_minutes: int
```

`dataclass` automatycznie generuje m.in. konstruktor i czytelny `repr`.

---

## 8. Praca z plikami

```python
text = "Python od zera"

with open("note.txt", "w", encoding="utf-8") as f:
    f.write(text)

with open("note.txt", "r", encoding="utf-8") as f:
    content = f.read()
    print(content)
```

---

## 9. Co dalej (proponowane elementy kursu)

Po tym tutorialu warto dodać/utrwalić:

1. **Typowanie i jakość kodu**
   - `typing` (`list[str]`, `dict[str, int]`),
   - podstawy formatowania kodu i czytelności.
2. **Podstawy testowania**
   - `pytest`,
   - proste testy funkcji (`assert`).
3. **Praca z danymi JSON**
   - `json.load`, `json.dump`.
4. **CLI i argumenty wejściowe**
   - `argparse`.
5. **Wstęp do walidacji danych**
   - `pydantic` (przyda się w dalszych labach AI).

---

## 10. Checklista przed wejściem w część AI

Powinieneś/powinnaś umieć:

- [ ] napisać i uruchomić skrypt `.py`,
- [ ] stworzyć funkcję z parametrami,
- [ ] użyć `if`, `for`, `while`,
- [ ] obsłużyć podstawowy wyjątek,
- [ ] stworzyć prostą klasę i obiekt,
- [ ] zapisać i odczytać dane z pliku.

Jeśli wszystko jest jasne, przejdź do [tutorial.md](tutorial.md) i [cwiczenia.md](cwiczenia.md).
