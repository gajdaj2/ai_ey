"""Lab 06 — Przykład 6: łączenie wielu middleware.

Middleware to klocki — można je składać. Kolejność ma znaczenie: middleware
"otaczają" wywołanie modelu w podanej kolejności (jak warstwy cebuli).

Ten agent łączy cztery zabezpieczenia naraz:

1. PIIMiddleware            — sanityzacja danych wrażliwych na wejściu,
2. SummarizationMiddleware — streszczanie długiej historii,
3. ModelCallLimitMiddleware — limit wywołań modelu (ochrona kosztów),
4. ToolRetryMiddleware      — ponowienia zawodnych narzędzi.

Uruchomienie:
    python labs/lab-06/solution/06_combined.py
"""

from __future__ import annotations

import os
from typing import Any

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.middleware import (
    AgentMiddleware,
    ModelCallLimitMiddleware,
    PIIMiddleware,
    SummarizationMiddleware,
    ToolRetryMiddleware,
)
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver

from tools import BASIC_TOOLS, reset_unstable_api, unstable_api

load_dotenv()

MODEL_NAME = "gpt-4o-mini"


def check_api_key() -> None:
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("Brak OPENAI_API_KEY. Ustaw zmienną środowiskową lub plik .env.")


def build_agent():
    """Agent z czterema middleware działającymi jednocześnie."""
    model = ChatOpenAI(model=MODEL_NAME, temperature=0)
    middleware: list[AgentMiddleware[Any, Any, Any]] = [
        PIIMiddleware("email", strategy="redact", apply_to_input=True),
        SummarizationMiddleware(model=MODEL_NAME, trigger=("messages", 8), keep=("messages", 3)),
        ModelCallLimitMiddleware(thread_limit=8, run_limit=6, exit_behavior="end"),
        ToolRetryMiddleware(max_retries=3, initial_delay=0.5, jitter=False),
    ]
    return create_agent(
        model,
        tools=[*BASIC_TOOLS, unstable_api],
        system_prompt="Jesteś bezpiecznym, odpornym asystentem. Odpowiadaj zwięźle i po polsku.",
        middleware=middleware,
        checkpointer=InMemorySaver(),
    )


def main() -> None:
    check_api_key()
    reset_unstable_api()
    agent = build_agent()
    config: RunnableConfig = {"configurable": {"thread_id": "combined-demo"}}

    print("=" * 60)
    print("  Łączenie middleware — PII + streszczanie + limity + retry")
    print("=" * 60)

    turns = [
        # Zawiera e-mail (zostanie zredagowany) i prośbę o zawodne narzędzie (retry).
        "Cześć, jestem Tomek (tomek@example.com). Pobierz dane dla 'pogoda jutro'.",
        "A teraz policz 12 * 12.",
        "Jaka jest pogoda w Krakowie?",
    ]

    for question in turns:
        result = agent.invoke({"messages": [{"role": "user", "content": question}]}, config)
        print(f"\nTy:    {question}")
        print(f"Agent: {result['messages'][-1].content}")

    print("\nWszystkie cztery middleware zadziałały w tle podczas tej rozmowy.")


if __name__ == "__main__":
    main()
