"""Lab 06 — Narzędzia (tools) współdzielone przez przykłady z middleware.

Każde narzędzie to zwykła funkcja Pythona z dekoratorem @tool. Docstring i type
hints są interfejsem, na podstawie którego model decyduje, kiedy i jak użyć
narzędzia.

Specjalne narzędzia na potrzeby labu:

- ``unstable_api`` — celowo zawodne narzędzie (rzuca wyjątek kilka pierwszych
  razy), żeby zademonstrować ``ToolRetryMiddleware``,
- ``send_email`` / ``read_email`` — akcja "niebezpieczna" i "bezpieczna" do
  demonstracji ``HumanInTheLoopMiddleware``.
"""

from __future__ import annotations

import ast
import operator
from datetime import datetime

from langchain_core.tools import tool

# ---------------------------------------------------------------------------
# Bezpieczny mini-kalkulator (jak w lab-05)
# ---------------------------------------------------------------------------

_ALLOWED_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def _safe_eval(node: ast.AST) -> float:
    """Rekurencyjnie i bezpiecznie ewaluuje wyrażenie arytmetyczne."""
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return float(node.value)
    if isinstance(node, ast.BinOp) and type(node.op) in _ALLOWED_OPERATORS:
        return _ALLOWED_OPERATORS[type(node.op)](_safe_eval(node.left), _safe_eval(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _ALLOWED_OPERATORS:
        return _ALLOWED_OPERATORS[type(node.op)](_safe_eval(node.operand))
    raise ValueError("Niedozwolone wyrażenie.")


@tool
def calculator(expression: str) -> str:
    """Wykonuje obliczenia matematyczne.

    Argument expression to wyrażenie arytmetyczne, np. "12 * 7 + 5".
    Obsługuje dodawanie, odejmowanie, mnożenie, dzielenie, potęgowanie i modulo.
    """
    try:
        tree = ast.parse(expression, mode="eval")
        return f"{expression} = {_safe_eval(tree.body)}"
    except Exception:
        return f"Nie udało się obliczyć wyrażenia: {expression!r}"


@tool
def get_current_time() -> str:
    """Zwraca aktualną datę i godzinę w formacie YYYY-MM-DD HH:MM:SS."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


@tool
def get_weather(city: str) -> str:
    """Zwraca aktualną (przykładową) pogodę dla podanego miasta."""
    sample = {
        "warszawa": "18°C, słonecznie",
        "gdańsk": "15°C, pochmurno, wiatr od morza",
        "kraków": "20°C, bezchmurnie",
    }
    return sample.get(city.lower().strip(), f"Brak danych pogodowych dla: {city}")


# ---------------------------------------------------------------------------
# Narzędzie zawodne — do demonstracji ToolRetryMiddleware
# ---------------------------------------------------------------------------

# Licznik nieudanych prób. Pierwsze _FAIL_TIMES wywołań rzuci wyjątek,
# a kolejne zakończą się sukcesem — dzięki temu widać, jak retry "ratuje" akcję.
_FAIL_TIMES = 2
_attempts = {"count": 0}


def reset_unstable_api() -> None:
    """Zeruje licznik prób narzędzia ``unstable_api`` (na potrzeby demo)."""
    _attempts["count"] = 0


@tool
def unstable_api(query: str) -> str:
    """Pobiera dane z (symulowanego) zawodnego, zewnętrznego API.

    Narzędzie celowo zawodzi kilka pierwszych razy (błąd sieci), aby pokazać
    działanie automatycznych ponowień (ToolRetryMiddleware).
    """
    _attempts["count"] += 1
    n = _attempts["count"]
    if n <= _FAIL_TIMES:
        raise ConnectionError(f"Tymczasowy błąd sieci (próba {n}). Spróbuj ponownie.")
    return f"OK (po {n} próbach): dane dla zapytania '{query}' zostały pobrane."


# ---------------------------------------------------------------------------
# Narzędzia "e-mail" — do demonstracji HumanInTheLoopMiddleware
# ---------------------------------------------------------------------------


@tool
def read_email(email_id: str) -> str:
    """Odczytuje treść e-maila o podanym identyfikatorze (akcja bezpieczna)."""
    return f"Treść e-maila {email_id}: 'Cześć, czy możemy przełożyć spotkanie?'"


@tool
def send_email(recipient: str, subject: str, body: str) -> str:
    """Wysyła e-mail (akcja NIEODWRACALNA — wymaga zgody człowieka).

    Args:
        recipient: adres odbiorcy.
        subject: temat wiadomości.
        body: treść wiadomości.
    """
    return f"E-mail wysłany do {recipient} z tematem '{subject}'."


# Gotowe zestawy narzędzi do użycia w przykładach
BASIC_TOOLS = [calculator, get_current_time, get_weather]
EMAIL_TOOLS = [read_email, send_email]
