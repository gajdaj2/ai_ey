"""Lab 06 — Przykład 4: HumanInTheLoopMiddleware (zgoda człowieka).

Middleware wstrzymuje wykonanie agenta tuż przed wywołaniem wskazanych narzędzi
i czeka na decyzję człowieka: zatwierdź (approve), edytuj (edit) lub odrzuć
(reject). Idealne do akcji nieodwracalnych (wysyłka e-maila, zapis do bazy,
płatność).

Wymaga ``checkpointer`` — stan jest zapamiętywany na czas przerwy (interrupt),
a następnie wznawiany komendą ``Command(resume=...)``.

Uruchomienie:
    python labs/lab-06/solution/04_human_in_the_loop.py
"""

from __future__ import annotations

import os

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command

from tools import EMAIL_TOOLS

load_dotenv()

MODEL_NAME = "gpt-4o-mini"


def check_api_key() -> None:
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("Brak OPENAI_API_KEY. Ustaw zmienną środowiskową lub plik .env.")


def build_agent():
    """Agent, który prosi o zgodę przed wysłaniem e-maila."""
    model = ChatOpenAI(model=MODEL_NAME, temperature=0)
    return create_agent(
        model,
        tools=EMAIL_TOOLS,
        system_prompt="Jesteś asystentem e-mail. Działaj zgodnie z prośbą użytkownika.",
        middleware=[
            HumanInTheLoopMiddleware(
                interrupt_on={
                    # send_email wymaga akceptacji (z opcją edycji i odrzucenia).
                    "send_email": {"allowed_decisions": ["approve", "edit", "reject"]},
                    # read_email jest bezpieczne — bez przerywania.
                    "read_email": False,
                },
                description_prefix="Akcja wymaga zatwierdzenia przez człowieka",
            ),
        ],
        checkpointer=InMemorySaver(),
    )


def ask_decision() -> dict:
    """Pyta operatora o decyzję i zwraca ją w formacie oczekiwanym przez middleware."""
    choice = input("Decyzja [a=zatwierdź / r=odrzuć]: ").strip().lower()
    if choice.startswith("r"):
        return {"type": "reject", "message": "Operator odrzucił wysyłkę."}
    return {"type": "approve"}


def main() -> None:
    check_api_key()
    agent = build_agent()
    config: RunnableConfig = {"configurable": {"thread_id": "hitl-demo"}}

    print("=" * 60)
    print("  HumanInTheLoopMiddleware — zgoda człowieka przed akcją")
    print("=" * 60)

    request = "Wyślij e-mail do szef@firma.pl z tematem 'Urlop' i treścią 'Proszę o urlop 1-5 lipca'."
    print(f"\nPolecenie: {request}\n")

    result = agent.invoke({"messages": [{"role": "user", "content": request}]}, config)

    # Jeżeli agent chce użyć narzędzia objętego kontrolą, bieg zostaje przerwany.
    while "__interrupt__" in result:
        for interrupt in result["__interrupt__"]:
            requests = interrupt.value if isinstance(interrupt.value, list) else [interrupt.value]
            for req in requests:
                actions = req.get("action_requests", []) if isinstance(req, dict) else []
                for action in actions:
                    print("⏸  Agent prosi o zgodę na akcję:")
                    print(f"     narzędzie: {action.get('name')}")
                    print(f"     argumenty: {action.get('args')}")

        decision = ask_decision()
        # Wznowienie biegu z decyzją człowieka.
        result = agent.invoke(
            Command(resume={"decisions": [decision]}),
            config,
        )

    print(f"\nOdpowiedź końcowa agenta:\n  {result['messages'][-1].content}")


if __name__ == "__main__":
    main()
