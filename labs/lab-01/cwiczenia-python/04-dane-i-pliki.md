# 04 — Struktury danych i pliki

## Cel

Przećwiczyć listy/słowniki oraz odczyt i zapis plików.

## Zadanie 1 — Lista słowników

Zdefiniuj listę uczestników:

```python
participants = [
    {"name": "Ala", "score": 82},
    {"name": "Bartek", "score": 67},
    {"name": "Celina", "score": 91},
]
```

Następnie:

- wypisz uczestników z wynikiem >= 80,
- policz średni wynik.

## Zadanie 2 — Zapis do pliku tekstowego

Zapisz raport do pliku `report.txt` w formacie:

```text
Ala: 82
Bartek: 67
Celina: 91
```

## Zadanie 3 — JSON

Zapisz tę samą listę do `participants.json` i odczytaj plik ponownie do zmiennej.

## Rozszerzenie

Dodaj obsługę wyjątków dla sytuacji:

- brak pliku,
- błędny format JSON.

## Oczekiwany efekt

Potrafisz pracować z danymi i plikami, co jest niezbędne w dalszych labach RAG/agentowych.
