"""
06_multi_turn_conversation.py — Konwersacja wieloobrotowa

Symuluje konwersację poprzez ręczne budowanie kontekstu
"""

from langchain_community.llms import Ollama
import json
from datetime import datetime

class SimpleConversation:
    def __init__(self, model_name="llama2"):
        self.llm = Ollama(model=model_name, temperature=0.7)
        self.history = []
    
    def chat(self, user_message: str) -> str:
        """Wysłij wiadomość i otrzymaj odpowiedź"""
        # Dodaj wiadomość użytkownika do historii
        self.history.append({"role": "user", "content": user_message})
        
        # Zbuduj kontekst
        context = self._build_context()
        
        # Otrzymaj odpowiedź
        response = self.llm.invoke(context)
        
        # Dodaj odpowiedź do historii
        self.history.append({"role": "assistant", "content": response})
        
        return response
    
    def _build_context(self) -> str:
        """Zbuduj prompt z historią konwersacji"""
        lines = []
        for msg in self.history:
            role = "Użytkownik" if msg["role"] == "user" else "Bot"
            lines.append(f"{role}: {msg['content']}")
        
        # Dodaj wskazówkę dla asystenta
        lines.append("Bot:")
        return "\n".join(lines)
    
    def save_conversation(self, filename: str):
        """Zapisz konwersację do JSON"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "model": "llama2",
                "conversations": self.history
            }, f, indent=2, ensure_ascii=False)
        print(f"✓ Konwersacja zapisana do {filename}")
    
    def print_conversation(self):
        """Wyświetl całą konwersację"""
        print("\n" + "=" * 70)
        print("Przebieg konwersacji:")
        print("=" * 70)
        
        for msg in self.history:
            role = "👤 Użytkownik" if msg["role"] == "user" else "🤖 Bot"
            print(f"\n{role}:")
            print(f"  {msg['content'][:200]}..." if len(msg['content']) > 200 else f"  {msg['content']}")

def main():
    print("=" * 70)
    print("Konwersacja wieloobrotowa z Ollama")
    print("=" * 70)
    
    # Utwórz konwersację
    conv = SimpleConversation()
    
    # Przykładowe wiadomości
    exchanges = [
        "Cześć! Jestem zainteresowany nauką programowania w Pythonie.",
        "Jakie są podstawowe koncepcje, które powinienem znać?",
        "Jak się różni Python od Java?",
        "Które biblioteki rekomendują do AI?",
        "Dziękuję za pomoc!"
    ]
    
    print("\n🤖 Rozmawiam z modelem...\n")
    
    for user_input in exchanges:
        print(f"👤 Użytkownik: {user_input}")
        response = conv.chat(user_input)
        # Pokaż pierwszą linię odpowiedzi
        first_line = response.split('\n')[0] if response else "Brak odpowiedzi"
        print(f"🤖 Bot: {first_line[:100]}...\n")
    
    # Wyświetl pełną konwersację
    conv.print_conversation()
    
    # Zapisz do pliku
    conv.save_conversation("/tmp/conversation.json")
    
    print("\n" + "=" * 70)
    print("✅ Gotowe!")
    print("\nWażna uwaga:")
    print("  Tego typu konwersacja ma ograniczoną pamięć,")
    print("  ponieważ każdorazowo wysyłamy całą historię.")
    print("  Dla produkcji rozważ użycie ConversationBufferMemory z LangChain.")

if __name__ == "__main__":
    main()
