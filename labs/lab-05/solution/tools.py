"""Narzędzia (tools) współdzielone przez agentów w lab-05.

Każde narzędzie to zwykła funkcja Pythona z dekoratorem @tool.
Docstring i type hints są interfejsem, na podstawie którego model
decyduje, kiedy i jak użyć narzędzia.
"""

from __future__ import annotations

import ast
import operator
from datetime import datetime

from langchain_core.tools import tool

# ---------------------------------------------------------------------------
# Prosta, bezpieczna baza wiedzy
# ---------------------------------------------------------------------------

KNOWLEDGE_BASE: dict[str, str] = {
    "langchain": (
        "LangChain to framework open-source do budowania aplikacji opartych na LLM. "
        "Udostępnia modele, prompty, parsery, retrievery i agentów."
    ),
    "agent": (
        "Agent AI to model LLM z dostępem do narzędzi, który samodzielnie decyduje, "
        "które narzędzie wywołać, aby rozwiązać zadanie użytkownika."
    ),
    "rag": (
        "RAG (Retrieval-Augmented Generation) to wzorzec, w którym model generuje "
        "odpowiedź na podstawie fragmentów pobranych z bazy wiedzy."
    ),
    "chromadb": (
        "ChromaDB to lokalna baza wektorowa w Pythonie, służąca do przechowywania "
        "embeddingów i wyszukiwania podobieństwa."
    ),
    "embedding": (
        "Embedding to wektor liczb reprezentujący semantyczne znaczenie tekstu. "
        "Teksty o podobnym znaczeniu mają bliskie sobie embeddingi."
    ),
}

# Bezpieczny zestaw operatorów dla mini-kalkulatora
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
        left = _safe_eval(node.left)
        right = _safe_eval(node.right)
        return _ALLOWED_OPERATORS[type(node.op)](left, right)
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
        result = _safe_eval(tree.body)
        return f"{expression} = {result}"
    except Exception:
        return f"Nie udało się obliczyć wyrażenia: {expression!r}"


@tool
def get_current_time() -> str:
    """Zwraca aktualną datę i godzinę w formacie YYYY-MM-DD HH:MM:SS."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


@tool
def search_knowledge_base(query: str) -> str:
    """Wyszukuje definicję pojęcia w lokalnej bazie wiedzy.

    Argument query to szukane pojęcie, np. "langchain", "rag", "agent".
    Zwraca krótką definicję lub informację, że pojęcia nie znaleziono.
    """
    key = query.lower().strip()
    for term, definition in KNOWLEDGE_BASE.items():
        if term in key or key in term:
            return definition
    return f"Nie znaleziono pojęcia '{query}' w bazie wiedzy."


# Lista narzędzi udostępniana agentom
TOOLS = [calculator, get_current_time, search_knowledge_base]
