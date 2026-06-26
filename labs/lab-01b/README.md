# Lab 01b — LangChain + Ollama (Modele lokalne)

Lab 01b to kontynuacja labu 01, w której zamiast API OpenAI użyjemy **Ollamy** — lokalnego narzędzia do uruchamiania dużych modeli językowych bez zależności od API i opłat.

## Zawartość

- `tutorial.md` — krótkie wprowadzenie do Ollamy i LangChain,
- `cwiczenia.md` — ćwiczenia praktyczne,
- `examples/` — gotowe przykłady do uruchomienia.

## Czym jest Ollama?

**Ollama** to narzędzie umożliwiające:
- **Lokalnie** uruchamiać duże modele językowe (LLM),
- **Bez klucza API** — wszystko działa na Twojej maszynie,
- **Szybko** przełączać między modelami (Llama 2, Mistral, Neural Chat itp.),
- **Integrować się** z LangChain poprzez `LangChain` community.

## Wymagania

1. **Zainstalowana Ollama** — pobierz z https://ollama.ai
2. **Python 3.10+** i aktywne środowisko wirtualne
3. **LangChain** i pakiety supportujące — patrz `requirements-lab01b.txt`
4. **Uruchomiony serwer Ollama** — domyślnie na `localhost:11434`

## Szybki start

### 1. Zainstaluj Ollama
```bash
# macOS / Linux
# Pobierz ze strony https://ollama.ai
# lub na Linuksie:
curl https://ollama.ai/install.sh | sh
```

### 2. Ściągnij model
```bash
ollama pull llama2      # ~4 GB
# lub mniejszy model:
ollama pull neural-chat # ~4 GB
```

### 3. Uruchom Ollama
```bash
ollama serve
```

Serwer będzie dostępny na `http://localhost:11434`

### 4. Zainstaluj zależności
```bash
pip install -r requirements-lab01b.txt
```

### 5. Uruchom pierwszy przykład
```bash
python examples/01_basic_ollama.py
```

## Rekomendowana ścieżka

1. Przeczytaj `tutorial.md` — poznaj Ollama i LangChain Ollama integration
2. Uruchom przykłady z folderu `examples/`
3. Wykonaj ćwiczenia z `cwiczenia.md`
4. Eksperymentuj z różnymi modelami i promptami

## Popularne modele w Ollamie

| Model | Rozmiar | Szybkość | Jakość |
|-------|---------|----------|--------|
| Neural Chat | ~4 GB | Szybki | Dobra |
| Llama 2 | ~4 GB | Średnia | Bardzo dobra |
| Mistral | ~5 GB | Szybki | Bardzo dobra |
| Orca Mini | ~2 GB | Szybki | Średnia |

## Porównanie: OpenAI vs Ollama (dla lab-01)

| Aspekt | OpenAI | Ollama |
|--------|--------|--------|
| **Setup** | Klucz API | Zainstalować + model |
| **Koszt** | $ za tokeny | Darmowe (komputer Twój) |
| **Szybkość** | Sieć | Lokalne (zależy od sprzętu) |
| **Privacy** | Dane wysyłane | Wszystko lokalnie |
| **Dostępność** | Wymaga internetu | Offline możliwe |

## Troubleshooting

### Błąd: "Cannot connect to Ollama server"
```bash
# Sprawdź czy Ollama jest uruchomiona
ollama serve
```

### Model się zawieszył
```bash
# Zmniejsz `top_k` lub zwiększ `temperature`
# Patrz tutorial.md sekcja "Parametry modelu"
```

### Za wolno / za dużo RAM
```bash
# Użyj mniejszego modelu
ollama pull neural-chat
# lub orca-mini
```

## Następne kroki

Po zrobieniu tego labu możesz:
- Przejść do lab-02 (FastAPI) i zbudować API z Ollama
- Lab-04 (RAG) — budować systemy RAG z lokalnymi modelami
- Lab-05 (Agenty) — tworzyć agenty z Ollama

---

**Powodzenia! 🚀**
