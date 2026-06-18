"""Lab 06 — Przykład 5: ToolRetryMiddleware (automatyczne ponowienia).

Gdy narzędzie rzuci wyjątek (np. chwilowy błąd sieci), middleware ponawia
wywołanie z rosnącym odstępem (exponential backoff). Buduje to odporność
agenta na przejściowe awarie zewnętrznych usług.

W demo narzędzie ``unstable_api`` zawodzi 2 pierwsze razy, a za trzecim razem
zwraca poprawny wynik — dzięki ponowieniom agent ostatecznie się udaje.

Uruchomienie:
    python labs/lab-06/solution/05_tool_retry.py
"""

from __future__ import annotations

import os

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.middleware import ToolRetryMiddleware
from langchain_openai import ChatOpenAI

from tools import reset_unstable_api, unstable_api

load_dotenv()

MODEL_NAME = "gpt-4o-mini"


def check_api_key() -> None:
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("Brak OPENAI_API_KEY. Ustaw zmienną środowiskową lub plik .env.")


def build_agent():
    """Agent z automatycznymi ponowieniami zawodnego narzędzia."""
    model = ChatOpenAI(model=MODEL_NAME, temperature=0)
    return create_agent(
        model,
        tools=[unstable_api],
        system_prompt=(
            "Jesteś asystentem. Aby pobrać dane, użyj narzędzia unstable_api. "
            "Jeśli narzędzie zwróci wynik, podaj go użytkownikowi."
        ),
        middleware=[
            ToolRetryMiddleware(
                max_retries=3,        # do 3 ponowień po pierwszej nieudanej próbie
                initial_delay=0.5,    # pierwszy odstęp: 0.5 s
                backoff_factor=2.0,   # kolejne odstępy rosną: 0.5 s, 1 s, 2 s...
                jitter=False,         # bez losowości — przewidywalne demo
            ),
        ],
    )


def main() -> None:
    check_api_key()
    reset_unstable_api()  # wyzeruj licznik prób przed demonstracją
    agent = build_agent()

    print("=" * 60)
    print("  ToolRetryMiddleware — odporność na chwilowe awarie narzędzia")
    print("=" * 60)
    print("\nNarzędzie unstable_api zawodzi 2 pierwsze razy, potem zwraca wynik.\n")

    request = "Pobierz dane dla zapytania 'kursy walut' przy użyciu narzędzia."
    result = agent.invoke({"messages": [{"role": "user", "content": request}]})

    print(f"Polecenie: {request}")
    print(f"\nOdpowiedź agenta (po automatycznych ponowieniach):\n  {result['messages'][-1].content}")


if __name__ == "__main__":
    main()
