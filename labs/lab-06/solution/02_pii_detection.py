"""Lab 06 — Przykład 2: PIIMiddleware (ochrona danych wrażliwych).

Middleware wykrywa dane osobowe (PII) w wiadomościach i stosuje wybraną
strategię: ``redact`` (zamień na etykietę), ``mask`` (zamaskuj część znaków),
``hash`` (zamień na skrót) albo ``block`` (zablokuj i zgłoś błąd).

Wbudowane typy PII: email, credit_card, ip, mac_address, url.

Uruchomienie:
    python labs/lab-06/solution/02_pii_detection.py
"""

from __future__ import annotations

import os

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.middleware import PIIMiddleware
from langchain_openai import ChatOpenAI

load_dotenv()

MODEL_NAME = "gpt-4o-mini"


def check_api_key() -> None:
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("Brak OPENAI_API_KEY. Ustaw zmienną środowiskową lub plik .env.")


def build_agent():
    """Agent, który sanityzuje dane wrażliwe w wiadomościach użytkownika."""
    model = ChatOpenAI(model=MODEL_NAME, temperature=0)
    return create_agent(
        model,
        tools=[],
        system_prompt="Jesteś asystentem obsługi klienta. Odpowiadaj krótko i po polsku.",
        middleware=[
            # E-mail zostanie zastąpiony etykietą [REDACTED_EMAIL].
            PIIMiddleware("email", strategy="redact", apply_to_input=True),
            # Numer karty zostanie częściowo zamaskowany.
            PIIMiddleware("credit_card", strategy="mask", apply_to_input=True),
            # Adres IP zostanie zastąpiony skrótem.
            PIIMiddleware("ip", strategy="hash", apply_to_input=True),
        ],
    )


def first_human_text(messages) -> str:
    """Zwraca treść pierwszej wiadomości użytkownika ze stanu agenta."""
    for msg in messages:
        if msg.__class__.__name__ == "HumanMessage":
            return msg.content if isinstance(msg.content, str) else str(msg.content)
    return ""


def main() -> None:
    check_api_key()
    agent = build_agent()

    print("=" * 60)
    print("  PIIMiddleware — sanityzacja danych wrażliwych na wejściu")
    print("=" * 60)

    sensitive = (
        "Mój e-mail to anna.kowalska@example.com, karta 4111 1111 1111 1111, "
        "a logowałam się z IP 192.168.10.42. Potwierdź, że dane zapisaliście."
    )
    print(f"\nORYGINALNE wejście użytkownika:\n  {sensitive}")

    result = agent.invoke({"messages": [{"role": "user", "content": sensitive}]})

    # Po przejściu przez middleware treść w stanie jest już zsanityzowana —
    # model NIE zobaczył surowych danych wrażliwych.
    print(f"\nWejście PO sanityzacji (to widzi model):\n  {first_human_text(result['messages'])}")
    print(f"\nOdpowiedź agenta:\n  {result['messages'][-1].content}")

    # ---------------------------------------------------------------
    # Strategia 'block' — całkowicie blokuje wiadomość z danym typem PII.
    # ---------------------------------------------------------------
    print("\n" + "-" * 60)
    print("  Strategia 'block' — twarde zablokowanie wiadomości z e-mailem")
    print("-" * 60)
    strict_agent = create_agent(
        ChatOpenAI(model=MODEL_NAME, temperature=0),
        tools=[],
        middleware=[PIIMiddleware("email", strategy="block", apply_to_input=True)],
    )
    try:
        strict_agent.invoke(
            {"messages": [{"role": "user", "content": "Napisz na jan@firma.pl"}]}
        )
        print("  (nie zablokowano — sprawdź konfigurację)")
    except Exception as exc:  # noqa: BLE001 — w demo pokazujemy typ błędu
        print(f"  Zablokowano zgodnie z polityką: {type(exc).__name__}: {exc}")


if __name__ == "__main__":
    main()
