"""Lab 05 — Agent AI z ręczną pętlą narzędzi (wersja edukacyjna).

Ten plik pokazuje, co dzieje się "pod maską" każdego agenta:
model wybiera narzędzie -> kod je wykonuje -> wynik wraca do modelu.
Pętla powtarza się, aż model udzieli finalnej odpowiedzi.
"""

from __future__ import annotations

import os

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langchain_openai import ChatOpenAI

from tools import TOOLS

load_dotenv()

MODEL_NAME = "gpt-4o-mini"
MAX_ITERATIONS = 6

SYSTEM_PROMPT = (
    "Jesteś pomocnym asystentem z dostępem do narzędzi. "
    "Używaj narzędzi, gdy są potrzebne do udzielenia dokładnej odpowiedzi. "
    "Do obliczeń ZAWSZE używaj narzędzia calculator zamiast liczyć samodzielnie. "
    "Odpowiadaj zwięźle i po polsku."
)


def check_api_key() -> None:
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("Brak OPENAI_API_KEY. Ustaw zmienną środowiskową lub plik .env.")


def run_agent(question: str) -> str:
    """Uruchamia ręczną pętlę agentową dla pojedynczego pytania."""
    tools_by_name = {t.name: t for t in TOOLS}
    model = ChatOpenAI(model=MODEL_NAME, temperature=0).bind_tools(TOOLS)

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=question),
    ]

    for _ in range(MAX_ITERATIONS):
        ai_message = model.invoke(messages)
        messages.append(ai_message)

        # Brak wywołań narzędzi = finalna odpowiedź
        if not ai_message.tool_calls:
            return str(ai_message.content)

        # Wykonaj każde narzędzie, o które poprosił model
        for tool_call in ai_message.tool_calls:
            selected_tool = tools_by_name[tool_call["name"]]
            print(f"  🔧 {tool_call['name']}({tool_call['args']})")
            observation = selected_tool.invoke(tool_call["args"])
            print(f"     ↳ {observation}")
            messages.append(
                ToolMessage(content=str(observation), tool_call_id=tool_call["id"])
            )

    return "Przekroczono maksymalną liczbę iteracji agenta."


def run_interactive() -> None:
    print("=" * 55)
    print("  Agent AI — ręczna pętla narzędzi (lab-05)")
    print("  Narzędzia: calculator, get_current_time, search_knowledge_base")
    print("  Wpisz pytanie lub 'q' żeby zakończyć.")
    print("=" * 55)

    while True:
        try:
            question = input("\nPytanie: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nDo widzenia!")
            break

        if question.lower() in {"q", "quit", "exit", "koniec"}:
            print("Do widzenia!")
            break

        if not question:
            continue

        print("\n[przebieg agenta]")
        answer = run_agent(question)
        print(f"\nOdpowiedź: {answer}")


def main() -> None:
    check_api_key()
    run_interactive()


if __name__ == "__main__":
    main()
