"""Lab 06 — Przykład 1: SummarizationMiddleware.

Automatycznie streszcza starszą część rozmowy, gdy historia rośnie, zachowując
kilka ostatnich wiadomości. Dzięki temu długie rozmowy nie przekraczają okna
kontekstu modelu i nie rosną w nieskończoność.

Uruchomienie:
    python labs/lab-06/solution/01_summarization.py
"""

from __future__ import annotations

import os

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.middleware import SummarizationMiddleware
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver

from tools import BASIC_TOOLS

load_dotenv()

MODEL_NAME = "gpt-4o-mini"


def check_api_key() -> None:
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("Brak OPENAI_API_KEY. Ustaw zmienną środowiskową lub plik .env.")


def build_agent():
    """Agent z middleware streszczającym długą historię rozmowy."""
    model = ChatOpenAI(model=MODEL_NAME, temperature=0)
    return create_agent(
        model,
        tools=BASIC_TOOLS,
        system_prompt="Jesteś pomocnym asystentem. Odpowiadaj krótko i po polsku.",
        middleware=[
            SummarizationMiddleware(
                model=MODEL_NAME,
                # Gdy liczba wiadomości osiągnie 6 — streść starsze...
                trigger=("messages", 6),
                # ...zachowując 2 ostatnie wiadomości w oryginale.
                keep=("messages", 2),
            ),
        ],
        # Checkpointer = pamięć wątku; pozwala prowadzić wieloturową rozmowę.
        checkpointer=InMemorySaver(),
    )


def main() -> None:
    check_api_key()
    agent = build_agent()
    config: RunnableConfig = {"configurable": {"thread_id": "summary-demo"}}

    # Scenariusz wieloturowy — z każdą turą historia rośnie i w pewnym momencie
    # zostanie automatycznie streszczona przez middleware.
    turns = [
        "Mam na imię Anna i uczę się LangChain.",
        "Policz proszę 23 * 19.",
        "Jaka jest pogoda w Gdańsku?",
        "A która jest teraz godzina?",
        "Podsumuj jednym zdaniem, czego do tej pory dotyczyła nasza rozmowa.",
        "Jak mam na imię i czego się uczę?",
    ]

    print("=" * 60)
    print("  SummarizationMiddleware — streszczanie długiej rozmowy")
    print("=" * 60)

    for question in turns:
        result = agent.invoke({"messages": [{"role": "user", "content": question}]}, config)
        messages = result["messages"]
        answer = messages[-1].content
        print(f"\nTy:    {question}")
        print(f"Agent: {answer}")
        # Liczba wiadomości w stanie pozostaje ograniczona dzięki streszczaniu.
        print(f"       [wiadomości w kontekście: {len(messages)}]")


if __name__ == "__main__":
    main()
