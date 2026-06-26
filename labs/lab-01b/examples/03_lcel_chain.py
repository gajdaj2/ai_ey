"""
03_lcel_chain.py — LCEL Chain z Ollama

Demonstracja łańcucha: prompt → model → parser
"""
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.llms import Ollama
from langchain_core.output_parsers import StrOutputParser

def main():
    print("=" * 70)
    print("LCEL Chain z Ollama")
    print("=" * 70)
    
    # Model
    print("\n1️⃣ Konfigurując model...")
    llm = Ollama(model="gemma3:12b", temperature=0.7)
    print("   ✓ Model gotowy")
    
    # Prompt
    print("2️⃣ Konfigurując prompt...")
    prompt = ChatPromptTemplate.from_template(
        "Wyjaśnij {temat} w prostych słowach (max 50 słów)."
    )
    print("   ✓ Prompt gotowy")
    
    # Parser
    print("3️⃣ Konfigurując parser...")
    parser = StrOutputParser()
    print("   ✓ Parser gotowy")
    
    # Łańcuch LCEL
    print("4️⃣ Budując łańcuch LCEL (prompt | llm | parser)...")
    chain = prompt | llm | parser
    print("   ✓ Łańcuch gotowy")
    
    # Uruchomienie
    topics = ["Python", "API REST", "Bazy danych", "Chmura obliczeniowa"]
    
    print("\n" + "=" * 70)
    print("Uruchamianie łańcucha dla różnych tematów:")
    print("=" * 70)
    
    for topic in topics:
        print(f"\n📚 Temat: {topic}")
        result = chain.invoke({"temat": topic})
        print(f"   Wyjaśnienie: {result}")
    
    print("\n" + "=" * 70)
    print("✅ Gotowe!")

if __name__ == "__main__":
    main()
