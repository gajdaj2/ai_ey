# 06 — Most do AI (przygotowanie do dalszej części labu)

## Cel

Połączyć podstawy Pythona z praktyką potrzebną w ćwiczeniach LangChain/OpenAI.

## Zadanie 1 — Konfiguracja środowiska

Sprawdź, czy masz:

- aktywne `venv`,
- zainstalowane pakiety z `requirements.txt`,
- ustawioną zmienną `OPENAI_API_KEY`.

Napisz krótki skrypt, który sprawdza obecność klucza środowiskowego przez `os.getenv` i wypisuje komunikat:

- `OK` (klucz ustawiony),
- `BRAK` (klucz nieustawiony).

## Zadanie 2 — Struktura wejścia

Przygotuj funkcję, która przyjmuje temat i poziom trudności, a zwraca słownik:

```python
{
  "topic": "...",
  "level": "...",
  "language": "pl"
}
```

To będzie format wejścia do późniejszych promptów.

## Zadanie 3 — Mini walidacja

Dodaj walidację:

- `level` musi być jednym z: `junior`, `mid`, `senior`,
- `topic` nie może być pusty.

W przypadku błędu rzuć `ValueError`.

## Rozszerzenie

Napisz prosty test (np. `pytest`) dla funkcji walidującej.

## Oczekiwany efekt

Masz gotowy fundament pod przejście do [../tutorial.md](../tutorial.md) i [../cwiczenia.md](../cwiczenia.md).
