"""
04_model_comparison.py — Porównanie modeli

Porównanie llama2 vs neural-chat
Wymaga: ollama pull neural-chat
"""

from langchain_community.llms import Ollama
import time

def compare_models():
    print("=" * 70)
    print("Porównanie modeli: llama2 vs neural-chat")
    print("=" * 70)
    
    models = ["llama2", "neural-chat"]
    prompt = "Czym zajmuje się DevOps inżynier?"
    
    print(f"\nPytanie: {prompt}\n")
    
    results = {}
    
    for model_name in models:
        print(f"🤖 Model: {model_name}")
        try:
            llm = Ollama(model=model_name, temperature=0.5)
            
            start = time.time()
            response = llm.invoke(prompt)
            elapsed = time.time() - start
            
            word_count = len(response.split())
            results[model_name] = {
                "time": elapsed,
                "response": response,
                "words": word_count
            }
            
            print(f"   ⏱️  Czas: {elapsed:.2f}s")
            print(f"   📝 Słowa: {word_count}")
            print(f"   Odpowiedź:")
            for line in response.split('\n')[:3]:  # Pokaż pierwsze 3 linie
                print(f"      {line}")
            print()
            
        except Exception as e:
            print(f"   ❌ Błąd: {e}")
            print(f"   Uwaga: Czy pobrałeś model? (ollama pull {model_name})")
            print()
    
    # Porównanie
    print("=" * 70)
    print("Porównanie:")
    print("=" * 70)
    
    if len(results) == 2:
        model1, model2 = results.keys()
        time1, time2 = results[model1]["time"], results[model2]["time"]
        
        faster = model1 if time1 < time2 else model2
        slower = model2 if time1 < time2 else model1
        
        print(f"\n⚡ Szybszy: {faster} ({results[faster]['time']:.2f}s)")
        print(f"🐢 Wolniejszy: {slower} ({results[slower]['time']:.2f}s)")
        print(f"   Różnica: {abs(time1 - time2):.2f}s")

if __name__ == "__main__":
    compare_models()
