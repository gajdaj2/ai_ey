from dotenv import load_dotenv
from fastapi import FastAPI


app = FastAPI()

load_dotenv()

from langchain_openai import ChatOpenAI
from pydantic import BaseModel
from langchain_core.prompts import ChatPromptTemplate

class Item(BaseModel):
    name: str
    description: str = None
    price: float


class Query(BaseModel):
    topic: str

@app.get("/")
def root():
    return {"message":"Hello, FastAPI!"}


@app.post("/query")
def query_llm(query: Query):
    model = ChatOpenAI(model="gpt-4o-mini",temperature=0.2)

    prompt = ChatPromptTemplate.from_messages([
        ("system", "Jesteś ekspertem od edukacji technicznej."),
        ("human", "Przygotuj krótkie wyjaśnienie pojęcia: {query}"),
    ])

    messages = prompt.invoke({"query":query})

    response = model.invoke(messages)
    return response.content




@app.get("/items/{item_id}")
def read_item(item_id: int):
    return {"item_id": item_id}

@app.get("/search")
def search(q: str, skip: int = 0, limit: int = 10):
    return {"query": q, "skip": skip, "limit": limit}


@app.post("/items")
def create_item(item: Item):
    return {
        "created":item
    }
