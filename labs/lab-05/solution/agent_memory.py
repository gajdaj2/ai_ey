"""Lab 05 — Agent AI z pamięcią (create_agent, LangChain v1).

Agent tworzony jest funkcją ``create_agent`` z pakietu ``langchain.agents``
(standard od LangChain 1.0). Pamięć rozmowy obsługuje wymienny backend:
InMemory albo SQLite — patrz ``memory.py``.
"""

from __future__ import annotations

import os

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_openai import ChatOpenAI

from memory import get_history
from tools import TOOLS

load_dotenv()

MODEL_NAME = "gpt-4o-mini"

SYSTEM_PROMPT = (
    "Jesteś pomocnym asystentem z dostępem do narzędzi. "
    "Używaj narzędzi, gdy są potrzebne do udzielenia dokładnej odpowiedzi. "
    "Do obliczeń ZAWSZE używaj narzędzia calculator zamiast liczyć samodzielnie. "
    "Pamiętasz wcześniejszy przebieg rozmowy. Odpowiadaj zwięźle i po polsku."
)


def check_api_key() -> None:
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("Brak OPENAI_API_KEY. Ustaw zmienną środowiskową lub plik .env.")


def build_agent():
    """Tworzy agenta LangChain z narzędziami i promptem systemowym."""
    model = ChatOpenAI(model=MODEL_NAME, temperature=0)
    return create_agent(model, tools=TOOLS, system_prompt=SYSTEM_PROMPT)


def chat(agent, history: BaseChatMessageHistory, question: str) -> str:
    """Dokłada pytanie do historii, wywołuje agenta i zapisuje odpowiedź.

    Cała dotychczasowa historia jest przekazywana do agenta jako kontekst,
    dzięki czemu agent „pamięta” wcześniejsze tury rozmowy.
    """
    history.add_user_message(question)
    result = agent.invoke({"messages": history.messages})
    answer = str(result["messages"][-1].content)
    history.add_ai_message(answer)
    return answer


def choose_backend() -> str:
    print("Wybierz rodzaj pamięci:")
    print("  [1] InMemory — ulotna (znika po zamknięciu programu)")
    print("  [2] SQLite   — trwała (plik agent_memory.db)")
    choice = input("Twój wybór [1/2]: ").strip()
    return "sqlite" if choice == "2" else "memory"


def run_interactive() -> None:
    agent = build_agent()
    backend = choose_backend()
    session_id = (
        input("Podaj identyfikator rozmowy (session_id) [domyślnie 'default']: ").strip()
        or "default"
    )
    history = get_history(backend, session_id)

    print("\n" + "=" * 55)
    print(f"  Agent AI z pamięcią — backend: {backend}, sesja: {session_id}")
    print("  Komendy: 'q' = wyjście, ':clear' = wyczyść pamięć sesji")
    print("=" * 55)

    if history.messages:
        print(f"  (wczytano {len(history.messages)} wiadomości z pamięci)")

    while True:
        try:
            question = input("\nTy: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nDo widzenia!")
            break

        if question.lower() in {"q", "quit", "exit", "koniec"}:
            print("Do widzenia!")
            break

        if question == ":clear":
            history.clear()
            print("Pamięć sesji wyczyszczona.")
            continue

        if not question:
            continue

        answer = chat(agent, history, question)
        print(f"Agent: {answer}")


def main() -> None:
    check_api_key()
    run_interactive()


if __name__ == "__main__":
    main()
