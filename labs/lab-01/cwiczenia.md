# Lab 01 — Ćwiczenia

> Te ćwiczenia dotyczą części LangChain. Jeśli potrzebujesz fundamentów Pythona, zacznij od `tutorial-python.md` i folderu `cwiczenia-python/`.

## Jak pracować z ćwiczeniami

Najlepiej wykonuj zadania po kolei. Każde kolejne rozwija poprzednie. Jeśli prowadzisz szkolenie, możesz potraktować sekcje 1–4 jako obowiązkowe, a 5–7 jako rozszerzenie.

---

## Ćwiczenie 1 — Pierwsze uruchomienie modelu

### Cel

Połącz się z modelem OpenAI przez `ChatOpenAI` i pobierz krótką odpowiedź tekstową.

### Zadanie

Napisz skrypt, który:

- tworzy obiekt `ChatOpenAI`,
- wysyła pytanie: `Czym jest LangChain?`,
- wypisuje odpowiedź na ekran.

### Wskazówka

Ustaw `temperature=0.2` i model `gpt-4o-mini`.

### Oczekiwany efekt

Program działa bez błędów i zwraca kilka zdań wyjaśnienia.

---

## Ćwiczenie 2 — Prompt z parametrem

### Cel

Użyj `ChatPromptTemplate`, aby zbudować prompt wielokrotnego użytku.

### Zadanie

Zbuduj prompt w stylu:

- system: `Jesteś trenerem technologii AI.`
- user: `Wyjaśnij pojęcie: {topic}`

Przetestuj go dla co najmniej 3 tematów:

- `LangChain`,
- `embeddingi`,
- `RAG`.

### Oczekiwany efekt

Dla każdego tematu otrzymujesz osobną, poprawną odpowiedź.

---

## Ćwiczenie 3 — Prosty łańcuch LCEL

### Cel

Połącz `prompt`, `model` i `StrOutputParser` w jeden pipeline.

### Zadanie

Zbuduj łańcuch, który dla podanej technologii wypisze:

- 3 zastosowania,
- 1 ryzyko wdrożeniowe,
- 1 rekomendację startową.

Wejście do łańcucha powinno być parametrem `technology`.

### Dodatkowe wymaganie

Odpowiedź ma być zwięzła i mieć maksymalnie 120 słów.

---

## Ćwiczenie 4 — Wymuszenie formatu odpowiedzi

### Cel

Naucz model odpowiadać w stałym układzie.

### Zadanie

Przygotuj prompt, który zwróci wynik dokładnie w formacie:

```text
Nazwa: ...
Opis: ...
Przykład: ...
```

Użyj tematu `agent AI`.

### Pytanie kontrolne

Czy model zawsze trzyma format idealnie? Jeśli nie, co można poprawić w promptcie?

---

## Ćwiczenie 5 — Generator ćwiczeń szkoleniowych

### Cel

Zastosuj poznane elementy do prostego use case'u edukacyjnego.

### Zadanie

Zbuduj łańcuch, który dla tematu wejściowego wygeneruje:

- krótki opis tematu,
- 3 pytania kontrolne,
- 1 mini-zadanie praktyczne.

Przetestuj dla tematu `prompt engineering`.

### Rozszerzenie

Dodaj drugi parametr: `poziom` (`junior`, `mid`, `senior`) i dostosuj trudność odpowiedzi.

---

## Ćwiczenie 6 — Porównanie temperatury

### Cel

Zobacz, jak temperatura wpływa na wynik.

### Zadanie

Uruchom ten sam prompt dwa razy:

- raz z `temperature=0`,
- raz z `temperature=0.8`.

Użyj polecenia: `Wymyśl 5 pomysłów na warsztat o LLM dla biznesu.`

### Do obserwacji

Porównaj:

- różnorodność odpowiedzi,
- powtarzalność,
- praktyczność pomysłów.

---

## Ćwiczenie 7 — Mini challenge

### Cel

Samodzielnie zaprojektuj małe narzędzie oparte o LangChain.

### Zadanie

Stwórz jedno z poniższych:

- generator planu nauki dla wybranego tematu,
- asystent do tworzenia pytań rekrutacyjnych,
- generator krótkich podsumowań artykułów technicznych.

### Minimalne wymagania

Rozwiązanie musi używać:

- `ChatPromptTemplate`,
- `ChatOpenAI`,
- operatora `|`,
- `StrOutputParser`.

### Kryteria oceny

- kod jest czytelny,
- prompt jest zrozumiały,
- wynik jest użyteczny biznesowo lub edukacyjnie.

---

## Zadanie dla prowadzącego

Jeśli prowadzisz szkolenie na żywo, możesz zakończyć lab szybką dyskusją:

- Kiedy sam prompt wystarcza, a kiedy trzeba budować pełny pipeline?
- Co jest największą zaletą LangChain względem bezpośredniego użycia SDK OpenAI?
- Jakie ograniczenia ma podejście `prompt | model | parser`?

---

## Sugestia rozwiązania organizacyjnego

Dobry układ pracy uczestnika:

1. stworzyć jeden plik roboczy,
2. po każdym ćwiczeniu dopisywać nową sekcję kodu,
3. testować na 2–3 różnych wejściach,
4. notować, które prompty dawały najlepsze rezultaty.

Powodzenia!
