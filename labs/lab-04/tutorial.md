# Lab 04 — Tutorial: RAG z LangChain i ChromaDB

## Cel labu

W tym labie zbudujesz pełny pipeline RAG (Retrieval-Augmented Generation), który:

- wczytuje i dzieli teksty na fragmenty (`chunks`),
- tworzy wektory embeddingów przez OpenAI,
- zapisuje je w lokalnej bazie wektorowej `ChromaDB`,
- wyszukuje najbardziej pasujące fragmenty na podstawie pytania użytkownika,
- generuje odpowiedź z **cytowaniem źródeł**.

Po wykonaniu labu uczestnik powinien umieć:

- wyjaśnić architekturę RAG,
- załadować dokumenty i podzielić je na chunki,
- zindeksować dokumenty w `ChromaDB`,
- zbudować łańcuch retrieval LCEL,
- uzyskać odpowiedź z metadanymi źródeł.

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

Uruchomienie gotowej aplikacji:

```bash
python labs/lab-04/solution/app.py
```

---

## 1. Czym jest RAG?

RAG to wzorzec, w którym model LLM **nie generuje odpowiedzi wyłącznie z pamięci treningowej**, ale najpierw wyszukuje relevantne fragmenty z bazy dokumentów, a dopiero potem generuje odpowiedź na ich podstawie.

Podstawowy przepływ:

```
Pytanie użytkownika
        │
        ▼
   Retriever: wyszukaj pasujące fragmenty w bazie wektorowej
        │
        ▼
   Prompt: "Odpowiedz na pytanie na podstawie kontekstu: {context}\n\nPytanie: {question}"
        │
        ▼
   LLM: generuje odpowiedź
        │
        ▼
   Odpowiedź + źródła
```

Zalety podejścia:

- model może odpowiadać na pytania o dane, których nie było w treningu,
- odpowiedzi są ugruntowane w konkretnych dokumentach,
- łatwiej audytować i wskazywać źródła.

---

## 2. Wczytywanie i dzielenie dokumentów

Tekst musi być podzielony na małe fragmenty, bo model embeddings ma limit tokenów, a retriever działa lepiej na krótszych, spójnych tematycznie kawałkach.

```python
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Wczytanie tekstu z pliku
with open("data/baza_wiedzy.txt", encoding="utf-8") as f:
    raw_text = f.read()

docs = [Document(page_content=raw_text, metadata={"source": "baza_wiedzy.txt"})]

splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=80,
)

chunks = splitter.split_documents(docs)
print(f"Liczba chunków: {len(chunks)}")
```

### Parametry splittera

- `chunk_size` — maksymalna liczba znaków w jednym fragmencie,
- `chunk_overlap` — liczba znaków wspólnych między sąsiednimi fragmentami (pomaga zachować kontekst),
- `RecursiveCharacterTextSplitter` najpierw próbuje dzielić po `\n\n`, potem `\n`, potem spacjach.

---

## 3. Tworzenie embeddingów i bazy ChromaDB

Embeddingi to wektory liczbowe reprezentujące semantyczne znaczenie tekstu. ChromaDB przechowuje je lokalnie i umożliwia szybkie wyszukiwanie podobieństwa.

```python
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

vectordb = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    persist_directory="./chroma_db",
    collection_name="lab04",
)

print(f"Zindeksowano {vectordb._collection.count()} fragmentów.")
```

### Co tu się dzieje?

- `OpenAIEmbeddings` wysyła każdy chunk do API OpenAI i dostaje wektor,
- `Chroma.from_documents` zapisuje wektory i tekst lokalnie w `./chroma_db/`,
- przy kolejnym uruchomieniu można załadować bazę bez ponownego indeksowania.

### Ponowne wczytanie istniejącej bazy

```python
vectordb = Chroma(
    persist_directory="./chroma_db",
    embedding_function=embeddings,
    collection_name="lab04",
)
```

---

## 4. Wyszukiwanie podobnych dokumentów

Retriever konwertuje pytanie na wektor i szuka najbliższych wektorów w bazie.

```python
retriever = vectordb.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 3},
)

docs = retriever.invoke("Czym jest LangChain?")
for doc in docs:
    print(doc.page_content[:200])
    print("Źródło:", doc.metadata.get("source"))
    print("---")
```

Parametr `k=3` oznacza: zwróć 3 najbardziej podobne fragmenty.

---

## 5. Budowanie łańcucha RAG z LCEL

Teraz łączymy retriever z modelem. To jest serce wzorca RAG.

```python
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI


def format_docs(docs):
    return "\n\n---\n\n".join(
        f"[{doc.metadata.get('source', 'brak')}]\n{doc.page_content}"
        for doc in docs
    )


prompt = ChatPromptTemplate.from_messages([
    ("system",
     "Jesteś pomocnym asystentem. Odpowiadaj wyłącznie na podstawie podanego kontekstu. "
     "Jeśli odpowiedź nie wynika z kontekstu, powiedz że nie wiesz."),
    ("human",
     "Kontekst:\n{context}\n\nPytanie: {question}"),
])

model = ChatOpenAI(model="gpt-4o-mini", temperature=0)

chain = (
    {
        "context": retriever | format_docs,
        "question": RunnablePassthrough(),
    }
    | prompt
    | model
    | StrOutputParser()
)
```

Wywołanie:

```python
answer = chain.invoke("Czym jest LangChain?")
print(answer)
```

---

## 6. Cytowanie źródeł

Standardowy łańcuch zwraca tylko tekst odpowiedzi. Jeśli chcesz też wiedzieć, które fragmenty zostały użyte, wywołaj retriever osobno:

```python
question = "Czym jest RAG?"

source_docs = retriever.invoke(question)
answer = chain.invoke(question)

print("Odpowiedź:\n", answer)
print("\nŹródła:")
for doc in source_docs:
    print(f"  - {doc.metadata.get('source')} | {doc.page_content[:120]}...")
```

---

## 7. Schemat gotowej aplikacji

Gotowa aplikacja w `solution/app.py` działa według tego schematu:

```
Uruchomienie
    │
    ├─ Sprawdź, czy ./chroma_db/ istnieje
    │      ├─ TAK → wczytaj istniejącą bazę
    │      └─ NIE → zaindeksuj dokumenty i zapisz
    │
    ├─ Zbuduj chain LCEL (retriever | prompt | model | parser)
    │
    └─ Pętla pytań
            │
            ├─ Pobierz pytanie od użytkownika
            ├─ Wywołaj chain i retriever
            ├─ Wypisz odpowiedź
            └─ Wypisz użyte źródła
```

---

## 8. Dobre praktyki

- używaj `chunk_overlap` — bez niego kontekst na granicy chunków bywa urwany,
- `k=3` to dobry punkt startowy; zbyt duże `k` rozmywa kontekst,
- przechowuj bazę wektorową na dysku (`persist_directory`), żeby nie płacić za embeddingi przy każdym uruchomieniu,
- instruuj model, żeby przyznał się do braku wiedzy zamiast halucynować,
- testuj retriever niezależnie od generacji — sprawdź, czy wyszukuje właściwe fragmenty.

---

## 9. Najczęstsze błędy

- brak `langchain-text-splitters` lub `chromadb` — sprawdź `pip list`,
- zbyt duże `chunk_size` — embeddingi tracą precyzję,
- indeksowanie za każdym razem od nowa — używaj `persist_directory`,
- brak instrukcji "nie wiesz" w prompcie — model halucynuje poza kontekstem.

---

## 10. Co dalej?

- RAG z wgrywaniem pliku PDF (`pypdf` + `PyPDFLoader`),
- wyszukiwanie MMR (Maximum Marginal Relevance) dla różnorodnych wyników,
- metadata filtering — odpowiadaj tylko z dokumentów określonej kategorii,
- integracja z Streamlit (lab-03) — chatbot z pamięcią RAG.
