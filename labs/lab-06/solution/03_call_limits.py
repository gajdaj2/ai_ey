"""Lab 06 — Przykład 3: limity wywołań (Model/Tool call limit).

Dwa middleware chroniące przed nadmiernymi kosztami i pętlami:

- ``ModelCallLimitMiddleware`` — ogranicza liczbę wywołań modelu,
- ``ToolCallLimitMiddleware`` — ogranicza liczbę wywołań narzędzi
  (globalnie albo dla konkretnego narzędzia).

``exit_behavior="end"`` powoduje, że po przekroczeniu limitu agent grzecznie
kończy bieg (zamiast rzucać wyjątek).

Uruchomienie:
    python labs/lab-06/solution/03_call_limits.py
"""

from __future__ import annotations

import os
from typing import Any

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.middleware import (
    AgentMiddleware,
    ModelCallLimitMiddleware,
    ToolCallLimitMiddleware,
)
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver

from tools import calculator

load_dotenv()

MODEL_NAME = "gpt-4o-mini"


def check_api_key() -> None:
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("Brak OPENAI_API_KEY. Ustaw zmienną środowiskową lub plik .env.")


def build_agent():
    """Agent z twardymi limitami liczby wywołań modelu i narzędzia."""
    model = ChatOpenAI(model=MODEL_NAME, temperature=0)
    # Typujemy listę bazową klasą AgentMiddleware — łączymy middleware o różnych
    # typach stanu (model-limit i tool-limit) w jednym agencie.
    middleware: list[AgentMiddleware[Any, Any, Any]] = [
        # Najwyżej 4 wywołania modelu w obrębie wątku.
        ModelCallLimitMiddleware(thread_limit=4, run_limit=4, exit_behavior="end"),
        # Najwyżej 2 wywołania narzędzia 'calculator' na pojedynczy bieg.
        ToolCallLimitMiddleware(
            tool_name="calculator",
            run_limit=2,
            exit_behavior="end",
        ),
    ]
    return create_agent(
        model,
        tools=[calculator],
        system_prompt=(
            "Jesteś asystentem. Każde działanie matematyczne wykonuj OSOBNYM "
            "wywołaniem narzędzia calculator, krok po kroku."
        ),
        middleware=middleware,
        checkpointer=InMemorySaver(),
    )


def main() -> None:
    check_api_key()
    agent = build_agent()
    config: RunnableConfig = {"configurable": {"thread_id": "limits-demo"}}

    print("=" * 60)
    print("  Model/Tool call limit — ochrona przed pętlą i kosztami")
    print("=" * 60)

    # Zadanie celowo wymaga wielu kroków — limit przerwie agenta wcześniej.
    question = (
        "Policz osobno: 2+2, potem 3*3, potem 10-4, a na końcu 100/5. "
        "Każde działanie policz oddzielnym wywołaniem narzędzia."
    )
    result = agent.invoke({"messages": [{"role": "user", "content": question}]}, config)

    tool_calls = sum(
        len(getattr(m, "tool_calls", []) or []) for m in result["messages"]
    )
    print(f"\nPytanie: {question}")
    print(f"\nLiczba wywołań narzędzia w przebiegu: {tool_calls} (limit narzędzia: 2)")
    print(f"Liczba wiadomości w stanie: {len(result['messages'])}")
    print(f"\nOstatnia wiadomość agenta:\n  {result['messages'][-1].content}")
    print(
        "\nWniosek: middleware zatrzymał agenta po osiągnięciu limitu, "
        "zamiast pozwolić mu liczyć w nieskończoność."
    )


if __name__ == "__main__":
    main()
