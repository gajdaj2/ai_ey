"""
01_basic_ollama.py — Pierwsze kroki z Ollama + LangChain

Wymagania:
  - Ollama uruchomiona: ollama serve
  - Model pobrany: ollama pull llama2
  - LangChain zainstalowany

Uruchomienie:
  python examples/01_basic_ollama.py
"""

from langchain_community.llms import Ollama

def main():
    print("=" * 60)
    print("Pierwsze kroki z Ollama + LangChain")
    print("=" * 60)
    
    # Utwórz instancję Ollama
    print("\n1️⃣ Tworzę połączenie z Ollama...")
    llm = Ollama(model="gemma3:12b", temperature=0.7)
    print("   ✓ Połączenie estabelione")
    
    # Prosty prompt
    print("\n2️⃣ Wysyłam zapytanie do modelu...")
    prompt = "Wyjaśnij w 3 zdaniach, czym jest sztuczna inteligencja."
    print(f"   Pytanie: {prompt}")
    
    response = llm.invoke(prompt)
    print(f"\n   Odpowiedź:")
    print(f"   {response}")
    
    # Drugie zapytanie
    print("\n" + "=" * 60)
    print("3️⃣ Drugie zapytanie...")
    prompt2 = "Jakie są popularne języki programowania do AI?"
    print(f"   Pytanie: {prompt2}")
    
    response2 = llm.invoke(prompt2)
    print(f"\n   Odpowiedź:")
    print(f"   {response2}")
    
    print("\n" + "=" * 60)
    print("✅ Gotowe!")

if __name__ == "__main__":
    main()

