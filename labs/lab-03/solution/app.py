from __future__ import annotations

import os

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

import streamlit as st

load_dotenv()

# ---------------------------------------------------------------------------
# Konfiguracja strony
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Lab 03 — Asystent AI",
    page_icon="🤖",
    layout="centered",
)

st.title("🤖 Asystent AI")
st.caption("Lab 03 — Streamlit + LangChain + OpenAI")

# ---------------------------------------------------------------------------
# Panel boczny z ustawieniami
# ---------------------------------------------------------------------------

with st.sidebar:
    st.header("⚙️ Ustawienia")

    if not os.getenv("OPENAI_API_KEY"):
        st.error("Brak OPENAI_API_KEY. Ustaw zmienną środowiskową lub plik .env.")
        st.stop()

    model_name = st.selectbox(
        "Model",
        ["gpt-4o-mini", "gpt-4o"],
        index=0,
    )

    temperature = st.slider(
        "Temperatura",
        min_value=0.0,
        max_value=1.0,
        value=0.2,
        step=0.1,
        help="Niska temperatura = bardziej przewidywalne odpowiedzi.",
    )

    system_prompt = st.text_area(
        "Prompt systemowy",
        value="Jesteś pomocnym asystentem AI prowadzącym rozmowę po polsku. "
              "Odpowiadaj zwięźle i konkretnie.",
        height=120,
    )

    st.divider()

    if st.button("🗑️ Wyczyść historię rozmowy", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.caption(f"Model: `{model_name}` · Temp: `{temperature}`")

# ---------------------------------------------------------------------------
# Inicjalizacja stanu sesji
# ---------------------------------------------------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

# ---------------------------------------------------------------------------
# Wyświetlenie historii rozmowy
# ---------------------------------------------------------------------------

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ---------------------------------------------------------------------------
# Obsługa nowej wiadomości od użytkownika
# ---------------------------------------------------------------------------

if user_input := st.chat_input("Napisz wiadomość..."):

    # Dopisanie wiadomości użytkownika do historii i wyświetlenie jej
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Budowanie listy wiadomości dla LangChain (system + cała historia)
    lc_messages: list = [SystemMessage(content=system_prompt)]
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            lc_messages.append(HumanMessage(content=msg["content"]))
        else:
            lc_messages.append(AIMessage(content=msg["content"]))

    # Strumieniowanie odpowiedzi modelu
    model = ChatOpenAI(model=model_name, temperature=temperature, streaming=True)

    def response_stream():
        for chunk in model.stream(lc_messages):
            yield chunk.content

    with st.chat_message("assistant"):
        response_text = st.write_stream(response_stream())

    # Zapisanie odpowiedzi modelu w historii
    st.session_state.messages.append({"role": "assistant", "content": response_text})
