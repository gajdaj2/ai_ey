# Lab 01b — Quick Start (5 minut)

## 🚀 Szybki Start

### 1. Zainstaluj Ollama
```bash
# macOS/Linux — pobierz z https://ollama.ai
# lub na Linuksie:
curl https://ollama.ai/install.sh | sh
```

### 2. Ściągnij model
```bash
ollama pull llama2
```

### 3. Uruchom serwer
```bash
ollama serve
# Powinieneś zobaczyć: "Serving on http://0.0.0.0:11434"
```

### 4. W nowym terminalu — zainstaluj pakiety
```bash
cd /Users/apple/szkolenia/ai_ey
pip install -r labs/lab-01b/requirements-lab01b.txt
```

### 5. Uruchom pierwszy przykład
```bash
python labs/lab-01b/examples/01_basic_ollama.py
```

**Oczekiwany output:**
```
============================================================
Pierwsze kroki z Ollama + LangChain
============================================================

1️⃣ Tworzę połączenie z Ollama...
   ✓ Połączenie estabelione

2️⃣ Wysyłam zapytanie do modelu...
   Pytanie: Wyjaśnij w 3 zdaniach, czym jest sztuczna inteligencja.

   Odpowiedź:
   Sztuczna inteligencja to gałąź informatyki...
```

---

## 📚 Struktura

```
lab-01b/
  ├── README.md              # Overview
  ├── tutorial.md            # Tutorial (przeczytaj najpierw)
  ├── cwiczenia.md           # 10 ćwiczeń
  ├── QUICKSTART.md          # Ten plik
  ├── requirements-lab01b.txt
  └── examples/
      ├── 01_basic_ollama.py           # Pierwsze kroki
      ├── 02_temperature_effect.py     # Parametry
      ├── 03_lcel_chain.py             # Łańcuchy
      ├── 04_model_comparison.py       # Porównanie modeli
      ├── 05_structured_output.py      # Pydantic
      └── 06_multi_turn_conversation.py # Multi-turn
```

---

## 🎯 Rekomendowana ścieżka

1. **Przeczytaj** `tutorial.md` (15 min)
2. **Uruchom** przykłady z `examples/` (10 min)
3. **Wykonaj** ćwiczenia 1-5 z `cwiczenia.md` (30 min)
4. **Eksperymentuj** i twórz własne projekty

---

## ✨ Popularne modele

```bash
ollama pull llama2           # 4GB — uniwersalny
ollama pull neural-chat      # 4GB — dobrze dostrojony
ollama pull mistral          # 5GB — szybki i mądry
ollama pull orca-mini        # 2GB — lekki
```

---

## 🐛 Troubleshooting

| Problem | Rozwiązanie |
|---------|------------|
| "Cannot connect" | Sprawdź `ollama serve` |
| "Model not found" | Uruchom `ollama pull llama2` |
| Zbyt wolno | Użyj mniejszego modelu |
| ImportError | `pip install langchain-community` |

---

## 📞 Potrzebujesz pomocy?

- Czytaj `tutorial.md` — wszystko tam jest wyjaśnione
- Patrz `cwiczenia.md` — wskazówki do każdego ćwiczenia
- Sprawdzaj `examples/` — gotowe rozwiązania

---

**Gotów? Zacznij od kroku 5! 🚀**
