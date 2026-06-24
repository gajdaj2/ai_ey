# 03 — Funkcje i moduły

## Cel

Nauczyć się rozbijać kod na mniejsze, wielokrotnego użytku elementy.

## Zadanie 1 — Funkcja użytkowa

Napisz funkcję:

```python
def normalize_text(text: str) -> str:
    ...
```

Funkcja ma:

- usunąć spacje z początku i końca (`strip()`),
- zamienić tekst na małe litery (`lower()`).

Przetestuj funkcję dla 3 różnych inputów.

## Zadanie 2 — Funkcja z argumentem domyślnym

Napisz funkcję:

```python
def shorten(text: str, max_len: int = 20) -> str:
    ...
```

Jeśli tekst jest dłuższy niż `max_len`, zwróć skróconą wersję zakończoną `...`.

## Zadanie 3 — Moduł

Utwórz plik `utils.py` i przenieś do niego funkcje z poprzednich zadań. W pliku `main.py` zaimportuj je i użyj.

## Rozszerzenie

Dodaj blok:

```python
if __name__ == "__main__":
    ...
```

i uruchamiaj program jako prosty CLI.

## Oczekiwany efekt

Masz kod podzielony na moduły i co najmniej 2 funkcje, które łatwo ponownie użyć.
