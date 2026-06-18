from __future__ import annotations

import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

load_dotenv()

MODEL_NAME = "gpt-4o-mini"

app = FastAPI(
    title="Lab 02 API",
    description="Proste API FastAPI z użyciem LangChain i OpenAI.",
    version="0.1.0",
)


class GenerateLessonRequest(BaseModel):
    topic: str = Field(min_length=3, description="Temat mikro-lekcji")
    audience: str = Field(default="junior python developer", description="Grupa odbiorców")
    max_words: int = Field(default=150, ge=50, le=400, description="Maksymalna liczba słów")


class GenerateLessonResponse(BaseModel):
    topic: str
    lesson: str


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


def create_chain():
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "Jesteś ekspertem od edukacji technicznej. Tworzysz krótkie, konkretne mikro-lekcje.",
            ),
            (
                "human",
                """
                Przygotuj mikro-lekcję dla odbiorcy: {audience}.

                Temat: {topic}
                Maksymalna długość: {max_words} słów

                Odpowiedź podziel dokładnie na sekcje:
                1. Definicja
                2. Przykład
                3. Najczęstszy błąd
                """,
            ),
        ]
    )

    model = ChatOpenAI(model=MODEL_NAME, temperature=0.2)
    parser = StrOutputParser()
    return prompt | model | parser


@app.post("/generate-lesson", response_model=GenerateLessonResponse)
def generate_lesson(payload: GenerateLessonRequest) -> GenerateLessonResponse:
    if not os.getenv("OPENAI_API_KEY"):
        raise HTTPException(status_code=500, detail="Brak OPENAI_API_KEY w środowisku.")

    chain = create_chain()
    lesson = chain.invoke(
        {
            "topic": payload.topic,
            "audience": payload.audience,
            "max_words": payload.max_words,
        }
    )
    return GenerateLessonResponse(topic=payload.topic, lesson=lesson)
