import json
import re

class XunoBot:
    def __init__(self):
        self.faq_content = self._load_faq()
        self.sections = self._parse_sections()
        
    def _load_faq(self):
        """Load the FAQ content from file"""
        try:
            with open("knowledge_base/faq.md", "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            return ""

    def _parse_sections(self):
        """Parse FAQ content into sections"""
        try:
            sections = []
            current_section = None
            current_items = []
            current_qa = None
            
            for line in self.faq_content.split('\n'):
                line = line.strip()
                
                # Skip empty lines
                if not line:
                    continue
                    
                # New section
                if line.startswith('### '):
                    if current_section and current_items:
                        sections.append({
                            'title': current_section,
                            'items': current_items
                        })
                    current_section = line.replace('### ', '')
                    current_items = []
                
                # Question
                elif line.startswith('**Q:'):
                    if current_qa:
                        current_items.append(current_qa)
                    current_qa = {
                        'question': line.replace('**Q:', '').replace('**', '').strip(),
                        'answer': ''
                    }
                
                # Answer
                elif line.startswith('A:') and current_qa:
                    current_qa['answer'] = line.replace('A:', '').strip()
                
                # Continue previous answer
                elif current_qa and current_qa['answer']:
                    current_qa['answer'] += ' ' + line
            
            # Add last QA pair and section
            if current_qa:
                current_items.append(current_qa)
            if current_section and current_items:
                sections.append({
                    'title': current_section,
                    'items': current_items
                })
            
            return sections
        except Exception as e:
            print(f"Error parsing sections: {str(e)}")
            return []

    def _format_answer(self, answer):
        """Format answer text with proper line breaks and bullet points"""
        # Split on bullet points and numbered items
        parts = re.split(r'(?:\d+\.|-)(?=\s)', answer)
        if len(parts) > 1:
            # If we have bullet points or numbers, format them nicely
            formatted = parts[0].strip()
            for i, part in enumerate(parts[1:], 1):
                formatted += f"\n • {part.strip()}"
            return formatted
        return answer

    def _find_best_match(self, question):
        """Find the best matching Q&A pair"""
        try:
            question_lower = question.lower()
            best_match = None
            best_score = 0
            
            # First try exact matches
            for section in self.sections:
                for item in section['items']:
                    if question_lower in item['question'].lower():
                        return {
                            'question': item['question'],
                            'answer': self._format_answer(item['answer'])
                        }
            
            # If no exact match, try word matching
            for section in self.sections:
                for item in section['items']:
                    # Count matching words
                    q_words = set(re.findall(r'\w+', item['question'].lower()))
                    question_words = set(re.findall(r'\w+', question_lower))
                    score = len(q_words.intersection(question_words))
                    
                    if score > best_score:
                        best_score = score
                        best_match = {
                            'question': item['question'],
                            'answer': self._format_answer(item['answer'])
                        }
            
            return best_match if best_score > 0 else None
        except Exception as e:
            print(f"Error finding match: {str(e)}")
            return None

    def _format_sections(self, sections):
        """Format sections with proper formatting for accordion display"""
        formatted_sections = []
        for section in sections:
            formatted_items = []
            for item in section['items']:
                formatted_items.append({
                    'question': item['question'],
                    'answer': self._format_answer(item['answer'])
                })
            formatted_sections.append({
                'title': section['title'],
                'items': formatted_items
            })
        return formatted_sections

    def ask(self, question: str) -> str:
        """Process a question and return a JSON response"""
        try:
            # Handle greetings
            greetings = ['hi', 'hello', 'hey']
            if question.lower().strip() in greetings:
                return json.dumps({
                    "type": "single_qa",
                    "question": "Welcome",
                    "answer": "Hi! I'm here to help you with information about Xuno's money transfer services. How can I assist you today?"
                }, indent=2)

            # Check for FAQ request
            if 'faq' in question.lower():
                return json.dumps({
                    "type": "accordion",
                    "sections": self._format_sections(self.sections)
                }, indent=2)
            
            # Find best matching question
            match = self._find_best_match(question)
            if match:
                return json.dumps({
                    "type": "single_qa",
                    "question": match['question'],
                    "answer": match['answer']
                }, indent=2)
            
            # If no match found, return a helpful error message
            return json.dumps({
                "type": "error",
                "message": "I couldn't find a specific answer to your question. You can:\n • Ask about our fees and rates\n • Learn about the transfer process\n • Check supported countries\n • Type 'faq' to see all available topics"
            }, indent=2)
            
        except Exception as e:
            return json.dumps({
                "type": "error",
                "message": f"Error processing question: {str(e)}"
            }, indent=2)

def main():
    bot = XunoBot()
    
    while True:
        try:
            question = input("\nYou: ").strip()
            if question.lower() in ['quit', 'exit']:
                break
                
            response = bot.ask(question)
            print("\nBot:", response)
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(json.dumps({
                "type": "error",
                "message": f"Error: {str(e)}"
            }, indent=2))

if __name__ == "__main__":
    main() 