class XunoBot:
    def __init__(self):
        self.faq_content = self._load_faq()
        
    def _load_faq(self):
        """Load the FAQ content from file"""
        try:
            with open("knowledge_base/faq.md", "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            print(f"Error loading FAQ: {str(e)}")
            return ""

    def _simple_faq_lookup(self, question: str) -> str:
        """
        Simple keyword-based FAQ lookup
        """
        try:
            # Split into Q&A sections
            sections = self.faq_content.split("**Q:")
            
            # Simple keyword matching
            question_lower = question.lower()
            best_match = None
            best_score = 0
            
            for section in sections[1:]:  # Skip first empty section
                q_end = section.find("**")
                a_start = section.find("A:") + 2
                
                if q_end != -1 and a_start != -1:
                    q = section[:q_end].strip()
                    a = section[a_start:].split("###")[0].strip()
                    
                    # Count matching words
                    score = sum(word in q.lower() for word in question_lower.split())
                    
                    if score > best_score:
                        best_score = score
                        best_match = f"Q: {q}\n{a}"
            
            return best_match if best_match else "I couldn't find a relevant answer in the FAQ."
            
        except Exception as e:
            return f"Error searching FAQ: {str(e)}"

    def ask(self, question: str) -> str:
        """
        Ask a question and get a response based on the FAQ knowledge base
        """
        return self._simple_faq_lookup(question)

def main():
    print("Initializing Xuno chatbot...")
    bot = XunoBot()
    print("Chatbot ready! Type 'quit' to exit.")
    
    while True:
        question = input("\nYou: ").strip()
        if question.lower() in ['quit', 'exit']:
            break
            
        response = bot.ask(question)
        print("\nBot:", response)

if __name__ == "__main__":
    main() 