from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()

# ---------------------------------------------------------------------------
# Ścieżki
# ---------------------------------------------------------------------------

BASE_DIR = Path(__file__).parent
DATA_FILE = BASE_DIR.parent / "data" / "baza_wiedzy.txt"
CHROMA_DIR = BASE_DIR / "chroma_db"
COLLECTION_NAME = "lab04"

# ---------------------------------------------------------------------------
# Konfiguracja modeli
# ---------------------------------------------------------------------------

EMBEDDING_MODEL = "text-embedding-3-small"
CHAT_MODEL = "gpt-4o-mini"


def check_api_key() -> None:
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("Brak OPENAI_API_KEY. Ustaw zmienną środowiskową lub plik .env.")


# ---------------------------------------------------------------------------
# Indeksowanie dokumentów
# ---------------------------------------------------------------------------

def load_and_split(path: Path) -> list[Document]:
    """Wczytuje plik tekstowy i dzieli go na chunki."""
    raw = path.read_text(encoding="utf-8")
    docs = [Document(page_content=raw, metadata={"source": path.name})]

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=80,
    )
    chunks = splitter.split_documents(docs)
    print(f"  Podzielono na {len(chunks)} chunków.")
    return chunks


def build_vectordb(embeddings: OpenAIEmbeddings) -> Chroma:
    """Tworzy nową bazę ChromaDB z pliku baza_wiedzy.txt."""
    print("Indeksuję dokumenty — to chwilę potrwa...")
    chunks = load_and_split(DATA_FILE)
    vectordb = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=str(CHROMA_DIR),
        collection_name=COLLECTION_NAME,
    )
    print(f"  Zapisano bazę w: {CHROMA_DIR}")
    return vectordb


def load_vectordb(embeddings: OpenAIEmbeddings) -> Chroma:
    """Wczytuje istniejącą bazę ChromaDB z dysku."""
    vectordb = Chroma(
        persist_directory=str(CHROMA_DIR),
        embedding_function=embeddings,
        collection_name=COLLECTION_NAME,
    )
    count = vectordb._collection.count()
    print(f"Wczytano bazę z dysku ({count} fragmentów).")
    return vectordb


def get_vectordb() -> Chroma:
    check_api_key()
    embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL)
    if CHROMA_DIR.exists() and any(CHROMA_DIR.iterdir()):
        return load_vectordb(embeddings)
    return build_vectordb(embeddings)


# ---------------------------------------------------------------------------
# Łańcuch RAG
# ---------------------------------------------------------------------------

def format_docs(docs: list[Document]) -> str:
    return "\n\n---\n\n".join(
        f"[Źródło: {doc.metadata.get('source', 'nieznane')}]\n{doc.page_content}"
        for doc in docs
    )


def build_chain(retriever):
    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            "Jesteś pomocnym asystentem. Odpowiadaj wyłącznie na podstawie podanego "
            "kontekstu. Jeśli odpowiedź nie wynika z kontekstu, powiedz że nie wiesz "
            "i nie próbuj zgadywać.",
        ),
        (
            "human",
            "Kontekst:\n{context}\n\nPytanie: {question}",
        ),
    ])

    model = ChatOpenAI(model=CHAT_MODEL, temperature=0)

    chain = (
        {
            "context": retriever | format_docs,
            "question": RunnablePassthrough(),
        }
        | prompt
        | model
        | StrOutputParser()
    )
    return chain


# ---------------------------------------------------------------------------
# Pętla pytań
# ---------------------------------------------------------------------------

def run_interactive(chain, retriever) -> None:
    print("\n" + "=" * 55)
    print("  RAG — Asystent z bazą wiedzy")
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

        # Pobierz fragmenty źródłowe
        source_docs = retriever.invoke(question)

        # Wygeneruj odpowiedź
        answer = chain.invoke(question)

        print("\nOdpowiedź:")
        print(answer)

        print("\nUżyte fragmenty:")
        for i, doc in enumerate(source_docs, 1):
            src = doc.metadata.get("source", "nieznane")
            preview = doc.page_content[:120].replace("\n", " ")
            print(f"  [{i}] {src}: {preview}...")


# ---------------------------------------------------------------------------
# Wejście
# ---------------------------------------------------------------------------

def main() -> None:
    vectordb = get_vectordb()
    retriever = vectordb.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 3},
    )
    chain = build_chain(retriever)
    run_interactive(chain, retriever)


if __name__ == "__main__":
    main()
