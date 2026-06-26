"""
05_structured_output.py — Strukturyzowany output z Pydantic

Użycie PydanticOutputParser do strukturyzowanych danych JSON
"""

from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field

class Book(BaseModel):
    """Model książki"""
    title: str = Field(description="Tytuł książki")
    author: str = Field(description="Autor")
    year: int = Field(description="Rok wydania")
    genre: str = Field(description="Gatunek")
    summary: str = Field(description="Krótki opis (max 30 słów)")

def main():
    print("=" * 70)
    print("Strukturyzowany output z Pydantic")
    print("=" * 70)
    
    # Parser
    parser = PydanticOutputParser(pydantic_object=Book)
    
    # Prompt z instrukcjami formatu
    prompt_text = """Zaproponuj książkę dotyczącą {topic}.
    
{format_instructions}

Odpowiedź musi być w formacie JSON."""
    
    prompt = PromptTemplate(
        template=prompt_text,
        input_variables=["topic"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )
    
    # Model
    llm = Ollama(model="llama2", temperature=0.5)
    
    # Łańcuch
    chain = prompt | llm | parser
    
    # Test dla różnych tematów
    topics = ["programowanie", "historia", "science fiction"]
    
    print("\n" + "=" * 70)
    print("Generowanie propozycji książek:")
    print("=" * 70)
    
    for topic in topics:
        print(f"\n📖 Temat: {topic}")
        try:
            result = chain.invoke({"topic": topic})
            print(f"   Tytuł: {result.title}")
            print(f"   Autor: {result.author}")
            print(f"   Rok: {result.year}")
            print(f"   Gatunek: {result.genre}")
            print(f"   Opis: {result.summary}")
        except Exception as e:
            print(f"   ❌ Błąd parsowania: {e}")
            print("   Wskazówka: Model może nie zwrócić poprawny JSON")
    
    print("\n" + "=" * 70)
    print("✅ Gotowe!")

if __name__ == "__main__":
    main()
