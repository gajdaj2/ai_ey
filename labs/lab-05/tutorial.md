# Lab 05 — Tutorial: AI Agenci z LangChain

## Cel labu

W tym labie zbudujesz agenta AI — model LLM, który potrafi **samodzielnie wybierać i wywoływać narzędzia** (tools), żeby rozwiązać zadanie użytkownika.

Po wykonaniu labu uczestnik powinien umieć:

- wyjaśnić, czym różni się agent od zwykłego chatu,
- zdefiniować narzędzie dekoratorem `@tool`,
- podpiąć narzędzia do modelu przez `bind_tools`,
- zrozumieć i zaimplementować pętlę agentową (reasoning → tool call → observation),
- użyć gotowego agenta z LangChain (`create_agent`),
- dodać pamięć rozmowy: InMemory oraz trwałą w bazie SQLite.

---

## Wymagania

- Python 3.10+
- aktywne środowisko wirtualne,
- ustawiony `OPENAI_API_KEY`,
- zainstalowane pakiety z `requirements.txt`.

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

Uruchomienie gotowych aplikacji:

```bash
# Wersja edukacyjna — ręczna pętla agentowa
python labs/lab-05/solution/app.py

# Agent create_agent (LangChain v1) z pamięcią InMemory lub SQLite
python labs/lab-05/solution/agent_memory.py
```

---

## 1. Czym jest agent AI?

Zwykły chat działa tak: pytanie → odpowiedź. Model korzysta wyłącznie z wiedzy treningowej i nie może wykonać żadnej akcji.

**Agent** to model, który dostał zestaw **narzędzi** i potrafi zdecydować:

- czy do odpowiedzi potrzebne jest jakieś narzędzie,
- które narzędzie wywołać i z jakimi argumentami,
- czy ma wystarczająco danych, żeby udzielić finalnej odpowiedzi.

Porównanie:

| Cecha | Zwykły chat | Agent |
|-------|-------------|-------|
| Źródło wiedzy | tylko trening | trening + narzędzia |
| Akcje | brak | wywołania narzędzi |
| Aktualne dane | nie | tak (np. API, baza, kalkulator) |
| Wieloetapowość | nie | tak (pętla rozumowania) |

---

## 2. Pętla agentowa (ReAct)

Agent działa w pętli — to wzorzec **ReAct** (Reasoning + Acting):

```
Pytanie użytkownika
        │
        ▼
   ┌─────────────────────────────┐
   │  LLM analizuje sytuację     │◄──────────┐
   └─────────────────────────────┘           │
        │                                     │
        ▼                                     │
   Czy potrzebne narzędzie?                   │
        │                                     │
   ┌────┴─────┐                               │
   │          │                               │
  TAK        NIE                              │
   │          │                               │
   ▼          ▼                               │
 Wywołaj   Zwróć finalną                      │
 narzędzie  odpowiedź                         │
   │                                          │
   ▼                                          │
 Wynik (observation) ──────────────────────────┘
 dołączony do kontekstu
```

Model wykonuje tę pętlę tyle razy, ile trzeba — może wywołać kilka narzędzi po kolei.

---

## 3. Definiowanie narzędzi

Narzędzie to zwykła funkcja Pythona z dekoratorem `@tool`. **Docstring jest ważny** — model czyta go, żeby zrozumieć, do czego służy narzędzie.

```python
from langchain_core.tools import tool


@tool
def add(a: float, b: float) -> float:
    """Dodaje dwie liczby i zwraca sumę."""
    return a + b


@tool
def multiply(a: float, b: float) -> float:
    """Mnoży dwie liczby i zwraca iloczyn."""
    return a * b
```

### Co model widzi w narzędziu?

- **nazwę** funkcji (`add`),
- **opis** z docstringa (`Dodaje dwie liczby...`),
- **schemat argumentów** z type hintów (`a: float, b: float`).

Dlatego dobra nazwa, docstring i typy są kluczowe — to z nich model decyduje, kiedy użyć narzędzia.

---

## 4. Podpinanie narzędzi do modelu

Metoda `bind_tools` informuje model, jakie narzędzia ma do dyspozycji:

```python
from langchain_openai import ChatOpenAI

tools = [add, multiply]
model = ChatOpenAI(model="gpt-4o-mini", temperature=0)
model_with_tools = model.bind_tools(tools)

response = model_with_tools.invoke("Ile to jest 12 razy 7?")
print(response.tool_calls)
```

Model **nie wykonuje** narzędzia sam — zwraca tylko informację, które narzędzie chce wywołać i z jakimi argumentami:

```python
[{'name': 'multiply', 'args': {'a': 12, 'b': 7}, 'id': 'call_abc123'}]
```

To **my** w kodzie wykonujemy narzędzie i odsyłamy wynik z powrotem do modelu.

---

## 5. Ręczna pętla agentowa

Teraz składamy całość. To pokazuje, co dzieje się "pod maską" każdego agenta:

```python
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langchain_openai import ChatOpenAI

tools = [add, multiply]
tools_by_name = {t.name: t for t in tools}

model = ChatOpenAI(model="gpt-4o-mini", temperature=0).bind_tools(tools)

messages = [
    SystemMessage(content="Jesteś asystentem, który liczy używając narzędzi."),
    HumanMessage(content="Ile to jest (12 * 7) + 5?"),
]

while True:
    ai_message = model.invoke(messages)
    messages.append(ai_message)

    # Brak wywołań narzędzi = mamy finalną odpowiedź
    if not ai_message.tool_calls:
        print(ai_message.content)
        break

    # Wykonaj każde narzędzie, o które poprosił model
    for tool_call in ai_message.tool_calls:
        selected_tool = tools_by_name[tool_call["name"]]
        observation = selected_tool.invoke(tool_call["args"])
        messages.append(
            ToolMessage(content=str(observation), tool_call_id=tool_call["id"])
        )
```

### Kluczowe elementy

- `ai_message.tool_calls` — lista narzędzi, które model chce wywołać,
- `ToolMessage` — wynik narzędzia odsyłany do modelu z `tool_call_id`,
- pętla kończy się, gdy model przestaje prosić o narzędzia.

---

## 6. Gotowy agent z `create_agent` (LangChain v1)

W praktyce nie piszesz pętli ręcznie. Od LangChain w wersji 1.0 standardowym sposobem tworzenia agentów jest funkcja `create_agent` z pakietu `langchain.agents`. Robi ona dokładnie to, co pętla z sekcji 5 — tylko za Ciebie.

```python
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI

model = ChatOpenAI(model="gpt-4o-mini", temperature=0)

agent = create_agent(
    model,
    tools=[add, multiply],
    system_prompt="Jesteś asystentem, który liczy używając narzędzi.",
)

result = agent.invoke(
    {"messages": [("user", "Ile to jest (12 * 7) + 5?")]}
)

print(result["messages"][-1].content)
```

`create_agent` zwraca gotowego agenta z wbudowaną pętlą narzędzi. Wejściem jest słownik z kluczem `messages`, a wynikiem — słownik, w którym ostatnia wiadomość zawiera finalną odpowiedź.

---

## 7. Pamięć agenta — dlaczego jej potrzebujesz

Domyślnie agent jest **bezstanowy** — każde wywołanie `invoke` to osobna rozmowa. Agent nie pamięta, co padło chwilę wcześniej:

```python
agent.invoke({"messages": [("user", "Mam na imię Bob.")]})
agent.invoke({"messages": [("user", "Jak mam na imię?")]})
# Agent nie wie — drugie wywołanie nie zna pierwszego.
```

Aby agent prowadził ciągłą rozmowę, musimy **przechowywać historię wiadomości** i dołączać ją do kolejnych wywołań.

Używamy do tego standardowego interfejsu LangChain `BaseChatMessageHistory`. Pokażemy dwie implementacje:

- **InMemory** — historia trzymana w pamięci procesu (znika po zamknięciu programu),
- **SQLite** — historia zapisywana w pliku bazy danych (przetrwa restart aplikacji).

Każda rozmowa ma swój `session_id` (identyfikator wątku), dzięki czemu jeden agent może obsługiwać wielu użytkowników niezależnie.

---

## 8. Pamięć InMemory

`InMemoryChatMessageHistory` to gotowa, lekka implementacja pamięci trzymanej w RAM. Idealna do prototypów i testów.

```python
from langchain_core.chat_history import InMemoryChatMessageHistory

history = InMemoryChatMessageHistory()
history.add_user_message("Mam na imię Bob.")
history.add_ai_message("Miło Cię poznać, Bob!")

print(history.messages)
# [HumanMessage('Mam na imię Bob.'), AIMessage('Miło Cię poznać, Bob!')]
```

Schemat rozmowy z agentem korzystającym z pamięci:

```python
def chat(agent, history, question: str) -> str:
    history.add_user_message(question)
    result = agent.invoke({"messages": history.messages})
    answer = result["messages"][-1].content
    history.add_ai_message(answer)
    return answer
```

Teraz agent zna kontekst:

```python
chat(agent, history, "Mam na imię Bob.")
print(chat(agent, history, "Jak mam na imię?"))  # "Masz na imię Bob."
```

Wadą jest ulotność — po zamknięciu programu cała historia znika.

---

## 9. Pamięć trwała w bazie SQLite

Aby rozmowa przetrwała restart aplikacji, zapisujemy wiadomości do bazy danych. Zostajemy przy czystym LangChain i tworzymy własną implementację `BaseChatMessageHistory` opartą o wbudowany moduł `sqlite3`.

```python
import json
import sqlite3

from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import BaseMessage, message_to_dict, messages_from_dict


class SQLiteChatMessageHistory(BaseChatMessageHistory):
    def __init__(self, session_id: str, db_path: str) -> None:
        self.session_id = session_id
        self.db_path = db_path
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS messages ("
                "id INTEGER PRIMARY KEY AUTOINCREMENT, "
                "session_id TEXT, message TEXT)"
            )

    @property
    def messages(self) -> list[BaseMessage]:
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                "SELECT message FROM messages WHERE session_id = ? ORDER BY id",
                (self.session_id,),
            ).fetchall()
        return messages_from_dict([json.loads(r[0]) for r in rows])

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
```

Najważniejsze: klasa implementuje ten sam interfejs `BaseChatMessageHistory` co wersja InMemory. Dzięki temu **kod agenta z sekcji 8 działa bez zmian** — wystarczy podmienić obiekt historii:

```python
history = SQLiteChatMessageHistory(session_id="bob", db_path="agent_memory.db")
chat(agent, history, "Mam na imię Bob.")

# ... zamknij program, uruchom ponownie ...

history = SQLiteChatMessageHistory(session_id="bob", db_path="agent_memory.db")
print(chat(agent, history, "Jak mam na imię?"))  # "Masz na imię Bob."
```

> LangChain udostępnia też gotowe `SQLChatMessageHistory` w pakiecie `langchain_community`. Własna implementacja jest tu celowo prosta i pokazuje, jak działa trwała pamięć od środka.

---

## 10. Narzędzia w gotowej aplikacji

W `solution/app.py` agent ma trzy narzędzia:

- `calculator` — wykonuje obliczenia matematyczne,
- `get_current_time` — zwraca aktualną datę i godzinę,
- `search_knowledge_base` — wyszukuje informacje w lokalnej bazie wiedzy.

Dzięki temu agent potrafi odpowiedzieć na pytania typu:

- *"Ile to jest 145 * 23?"* → użyje `calculator`,
- *"Która jest godzina?"* → użyje `get_current_time`,
- *"Czym jest LangChain?"* → użyje `search_knowledge_base`,
- *"Która godzina i ile to 7*7?"* → użyje **dwóch** narzędzi po kolei.

---

## 11. System prompt agenta

System prompt definiuje "osobowość" i zasady działania agenta:

```python
SYSTEM_PROMPT = (
    "Jesteś pomocnym asystentem z dostępem do narzędzi. "
    "Używaj narzędzi, gdy są potrzebne do udzielenia dokładnej odpowiedzi. "
    "Do obliczeń ZAWSZE używaj narzędzia calculator zamiast liczyć samodzielnie. "
    "Odpowiadaj zwięźle i po polsku."
)
```

Dobre praktyki promptu agenta:

- jasno powiedz, **kiedy** używać narzędzi,
- wymuś użycie narzędzia tam, gdzie model bywa zawodny (np. matematyka),
- ustaw język i styl odpowiedzi.

---

## 12. Obserwacja działania agenta

Żeby zrozumieć decyzje agenta, warto wypisywać każdy krok pętli:

```python
for tool_call in ai_message.tool_calls:
    print(f"🔧 Agent wywołuje: {tool_call['name']}({tool_call['args']})")
    observation = selected_tool.invoke(tool_call["args"])
    print(f"   ↳ wynik: {observation}")
```

To bardzo pomaga w nauce i debugowaniu — widać, jak model "myśli".

---

## 13. Dobre praktyki

- pisz **precyzyjne docstringi** — to interfejs między modelem a narzędziem,
- używaj `temperature=0` dla agentów — chcesz przewidywalnych decyzji,
- waliduj argumenty narzędzi (type hints + ewentualnie Pydantic),
- ogranicz liczbę iteracji pętli, żeby uniknąć nieskończonych wywołań,
- loguj wywołania narzędzi — to Twój wgląd w rozumowanie agenta,
- nie ufaj ślepo narzędziom destrukcyjnym (np. usuwanie plików) — dodaj potwierdzenie.

---

## 14. Najczęstsze błędy

- brak docstringa w narzędziu — model nie wie, kiedy go użyć,
- zbyt ogólne nazwy narzędzi (`tool1`, `do_stuff`),
- brak limitu iteracji — ryzyko pętli w nieskończoność,
- wysoka temperatura — agent podejmuje chaotyczne decyzje,
- zapominanie o odesłaniu `ToolMessage` z `tool_call_id` w ręcznej pętli.

---

## 15. Co dalej?

- **human-in-the-loop** — agent pyta o zgodę przed akcją,
- **pamięć długoterminowa** — wektorowa pamięć faktów o użytkowniku (np. oparta o lab-04),
- **RAG jako narzędzie** — połącz lab-04 (retriever) jako tool agenta,
- **multi-agent** — kilku agentów współpracujących nad zadaniem,
- **agent w API/UI** — opakuj agenta w FastAPI (lab-02) lub Streamlit (lab-03).

Gotowe implementacje znajdziesz w `solution/app.py` oraz `solution/agent_memory.py`.
