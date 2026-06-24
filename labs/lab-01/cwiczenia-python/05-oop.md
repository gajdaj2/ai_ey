# 05 — OOP w praktyce

## Cel

Zrozumieć klasy, obiekty, dziedziczenie i kompozycję.

## Zadanie 1 — Klasa bazowa

Utwórz klasę `Course` z polami:

- `title`,
- `level`,
- `duration_hours`.

Dodaj metodę `summary()`, która zwróci zwięzły opis kursu.

## Zadanie 2 — Dziedziczenie

Utwórz klasę `AICourse(Course)`, która dodaje pole `framework` (np. `LangChain`).

Nadpisz `summary()` tak, aby zawierała również framework.

## Zadanie 3 — Kompozycja

Utwórz klasę `Instructor` (`name`, `experience_years`) i podepnij ją do `Course` jako atrybut.

## Rozszerzenie

Zrób wersję klasy `Instructor` z `@dataclass` i porównaj czytelność kodu.

## Oczekiwany efekt

Potrafisz modelować prostą domenę biznesową z użyciem OOP.
