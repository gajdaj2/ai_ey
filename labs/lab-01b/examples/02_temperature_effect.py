"""
02_temperature_effect.py — Wpływ parametrów na odpowiedzi

Porównuje odpowiedzi z różnymi wartościami temperature i top_k.
Pokazuje, jak parametry wpływają na kreatywność modelu.
"""

from langchain_community.llms import Ollama
import time

def main():
    print("=" * 70)
    print("Wpływ parametrów na odpowiedzi Ollama")
    print("=" * 70)
    
    prompt = "Wymyśl kreatywne nazwy dla startup'u z AI"
    
    # Test różnych temperatur
    temperatures = [0.1, 0.5, 0.9, 1.5]
    
    print(f"\nPytanie: {prompt}\n")
    print("Testowanie różnych temperatur:")
    print("-" * 70)
    
    for temp in temperatures:
        print(f"\n🌡️ Temperature = {temp}")
        llm = Ollama(model="llama2", temperature=temp)
        
        start = time.time()
        response = llm.invoke(prompt)
        elapsed = time.time() - start
        
        # Pokazuj pierwszą linię odpowiedzi
        first_line = response.split('\n')[0] if response else "Brak odpowiedzi"
        print(f"   Czas: {elapsed:.2f}s")
        print(f"   Odpowiedź: {first_line[:80]}...")
    
    # Test top_k
    print("\n" + "=" * 70)
    print("Testowanie różnych wartości top_k (temperature=0.7):")
    print("-" * 70)
    
    top_ks = [5, 20, 50, 100]
    
    for top_k in top_ks:
        print(f"\n📊 top_k = {top_k}")
        llm = Ollama(model="llama2", temperature=0.7, top_k=top_k)
        
        start = time.time()
        response = llm.invoke(prompt)
        elapsed = time.time() - start
        
        first_line = response.split('\n')[0] if response else "Brak odpowiedzi"
        print(f"   Czas: {elapsed:.2f}s")
        print(f"   Odpowiedź: {first_line[:80]}...")
    
    print("\n" + "=" * 70)
    print("✅ Gotowe!")
    print("\nWnioski:")
    print("  • Wyższa temperatura = bardziej twórcze odpowiedzi")
    print("  • Niższy top_k = bardziej deterministyczne odpowiedzi")
    print("  • Eksperymentuj, aby znaleźć idealne ustawienia!")

if __name__ == "__main__":
    main()
