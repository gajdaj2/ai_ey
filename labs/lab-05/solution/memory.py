"""Lab 05 — Zarządzanie pamięcią rozmowy agenta.

Dwie implementacje wspólnego interfejsu LangChain ``BaseChatMessageHistory``:

- InMemory — historia trzymana w pamięci procesu (ulotna),
- SQLite   — historia zapisywana do pliku bazy danych (trwała).

Dzięki wspólnemu interfejsowi kod agenta jest identyczny niezależnie od
wybranego backendu pamięci.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from langchain_core.chat_history import (
    BaseChatMessageHistory,
    InMemoryChatMessageHistory,
)
from langchain_core.messages import BaseMessage, message_to_dict, messages_from_dict

BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / "agent_memory.db"

# Współdzielony magazyn historii InMemory — jeden obiekt na sesję,
# utrzymywany przez cały czas życia procesu.
_MEMORY_STORE: dict[str, InMemoryChatMessageHistory] = {}


class SQLiteChatMessageHistory(BaseChatMessageHistory):
    """Trwała historia rozmowy zapisywana w bazie SQLite.

    Implementuje ten sam interfejs co InMemoryChatMessageHistory, więc można
    jej używać zamiennie. Każda wiadomość jest serializowana do JSON i zapisana
    w tabeli ``messages`` z przypisanym ``session_id``.
    """

    def __init__(self, session_id: str, db_path: str | Path = DB_PATH) -> None:
        self.session_id = session_id
        self.db_path = str(db_path)
        self._ensure_table()

    def _ensure_table(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    message TEXT NOT NULL
                )
                """
            )

    @property
    def messages(self) -> list[BaseMessage]:
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                "SELECT message FROM messages WHERE session_id = ? ORDER BY id",
                (self.session_id,),
            ).fetchall()
        return messages_from_dict([json.loads(row[0]) for row in rows])

    def add_message(self, message: BaseMessage) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO messages (session_id, message) VALUES (?, ?)",
                (self.session_id, json.dumps(message_to_dict(message))),
            )

    def clear(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "DELETE FROM messages WHERE session_id = ?", (self.session_id,)
            )


def get_history(backend: str, session_id: str) -> BaseChatMessageHistory:
    """Zwraca obiekt historii dla wybranego backendu pamięci.

    Args:
        backend: ``"memory"`` (ulotna) lub ``"sqlite"`` (trwała).
        session_id: identyfikator rozmowy/wątku.
    """
    if backend == "memory":
        if session_id not in _MEMORY_STORE:
            _MEMORY_STORE[session_id] = InMemoryChatMessageHistory()
        return _MEMORY_STORE[session_id]

    if backend == "sqlite":
        return SQLiteChatMessageHistory(session_id)

    raise ValueError(
        f"Nieznany backend pamięci: {backend!r}. Użyj 'memory' lub 'sqlite'."
    )
