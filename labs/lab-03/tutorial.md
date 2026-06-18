# Lab 03 — Tutorial: Streamlit + LangChain + OpenAI

## Cel labu

W tym labie zbudujesz aplikację chatową w `Streamlit`, która:

- prowadzi rozmowę z modelem OpenAI przez `LangChain`,
- przechowuje historię wiadomości w sesji,
- strumieniuje odpowiedź modelu słowo po słowie,
- pozwala zmieniać prompt systemowy i temperaturę przez panel boczny.

Po wykonaniu labu uczestnik powinien umieć:

- zbudować prosty interfejs Streamlit,
- korzystać z `st.chat_message` i `st.chat_input`,
- trzymać stan aplikacji w `st.session_state`,
- zintegrować `ChatOpenAI` ze strumieniowaniem w Streamlit,
- parametryzować aplikację przez `st.sidebar`.

---

## Wymagania

- Python 3.10+
- aktywne środowisko wirtualne,
- ustawiony `OPENAI_API_KEY`,
- zainstalowane pakiety z `requirements.txt`.

Szybkie uruchomienie środowiska:

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

lub z `uv`:

```bash
uv pip install -r requirements.txt
```

---

## 1. Czym jest Streamlit?

`Streamlit` to framework, który zamienia zwykły skrypt Pythona w interaktywną aplikację webową — bez HTML i JavaScript.

Kod wykonuje się od góry do dołu przy każdej interakcji użytkownika. Stan między uruchomieniami trzyma się w `st.session_state`.

Minimalny serwer:

```python
import streamlit as st

st.title("Moja aplikacja")
st.write("Witaj na warsztacie AI!")
```

Uruchomienie:

```bash
streamlit run labs/lab-03/solution/app.py
```

Streamlit automatycznie otwiera przeglądarkę pod `http://localhost:8501`.

---

## 2. Podstawowe elementy interfejsu

Najczęściej używane komponenty:

```python
import streamlit as st

# Tytuły i tekst
st.title("Tytuł")
st.write("Tekst lub obiekt Pythona")
st.markdown("**Pogrubiony** tekst")

# Wejście od użytkownika
name = st.text_input("Twoje imię:")
temperature = st.slider("Temperatura", 0.0, 1.0, 0.2, step=0.1)

# Przycisk i akcja
if st.button("Generuj"):
    st.write(f"Hej, {name}!")

# Panel boczny
with st.sidebar:
    st.header("Ustawienia")
    model = st.selectbox("Model", ["gpt-4o-mini", "gpt-4o"])
```

---

## 3. Historia rozmowy z `st.session_state`

`session_state` to słownik przechowywany między przeładowaniami strony.

Wzorzec inicjalizacji historii wiadomości:

```python
import streamlit as st

if "messages" not in st.session_state:
    st.session_state.messages = []
```

Wyświetlenie historii:

```python
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
```

Każda wiadomość jest słownikiem z kluczami `role` (`user` lub `assistant`) i `content`.

---

## 4. Pole wejściowe czatu

`st.chat_input` blokuje dalsze wykonanie, jeśli użytkownik nic nie wpisał.

```python
if prompt := st.chat_input("Napisz wiadomość..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
```

---

## 5. Integracja z LangChain i OpenAI

Zamiast budować listę wiadomości ręcznie, możemy przekazać historię z `session_state` do `ChatOpenAI`:

```python
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

model = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)

# Budowanie listy wiadomości dla modelu
lc_messages = [SystemMessage(content="Jesteś pomocnym asystentem.")]

for msg in st.session_state.messages:
    if msg["role"] == "user":
        lc_messages.append(HumanMessage(content=msg["content"]))
    else:
        lc_messages.append(AIMessage(content=msg["content"]))

response = model.invoke(lc_messages)
```

---

## 6. Strumieniowanie odpowiedzi

Streamlit ma wbudowane wsparcie dla generatorów przez `st.write_stream`.

Łączymy to z metodą `.stream()` z LangChain:

```python
def stream_response(messages):
    model = ChatOpenAI(model="gpt-4o-mini", temperature=0.2, streaming=True)
    for chunk in model.stream(messages):
        yield chunk.content
```

W interfejsie:

```python
with st.chat_message("assistant"):
    response = st.write_stream(stream_response(lc_messages))

st.session_state.messages.append({"role": "assistant", "content": response})
```

Efekt: tekst pojawia się na ekranie słowo po słowie, co wygląda jak typowanie.

---

## 7. Panel boczny z ustawieniami

Sidebar pozwala użytkownikowi dostosować działanie aplikacji bez edycji kodu:

```python
with st.sidebar:
    st.header("⚙️ Ustawienia")
    system_prompt = st.text_area(
        "Prompt systemowy",
        value="Jesteś pomocnym asystentem AI.",
        height=120,
    )
    temperature = st.slider("Temperatura", 0.0, 1.0, 0.2, step=0.1)
    model_name = st.selectbox("Model", ["gpt-4o-mini", "gpt-4o"])

    if st.button("🗑️ Wyczyść historię"):
        st.session_state.messages = []
        st.rerun()
```

---

## 8. Pełny przepływ aplikacji

Gotowa aplikacja w `solution/app.py` działa według tego schematu:

```
Uruchomienie
    │
    ├─ Sidebar: ustaw model / temperaturę / prompt systemowy
    │
    ├─ Wyświetl historię wiadomości z session_state
    │
    └─ Wejście użytkownika (st.chat_input)
            │
            ├─ Dopisz user message do session_state
            │
            ├─ Zbuduj listę wiadomości LangChain (system + historia + nowa)
            │
            ├─ Wywołaj model z streamingiem
            │
            └─ Dopisz odpowiedź do session_state
```

---

## 9. Uruchomienie gotowej aplikacji

```bash
source .venv/bin/activate
streamlit run labs/lab-03/solution/app.py
```

Otworzy się przeglądarka z aplikacją czatu pod `http://localhost:8501`.

---

## 10. Dobre praktyki

- inicjalizuj `session_state` na początku, przed wyświetleniem czegokolwiek,
- nie twórz obiektu modelu przy każdym wywołaniu — używaj `@st.cache_resource`,
- trzymaj prompt systemowy oddzielnie od historii rozmowy,
- zawsze dodawaj przycisk "wyczyść historię",
- `st.rerun()` wymusza przeładowanie strony po wyczyszczeniu stanu.

---

## 11. Co dalej?

Po tym labie naturalnym krokiem jest:

- dodanie RAG (wgrywanie pliku PDF i odpowiedzi z cytowaniem),
- wielokrotne persony / różne prompty systemowe,
- eksport historii do pliku,
- wdrożenie na Streamlit Cloud.
