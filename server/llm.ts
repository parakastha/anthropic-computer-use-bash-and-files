import Anthropic from '@anthropic-ai/sdk';
import path from 'path';
import fs from 'fs';

// Define types for FAQ data structures
interface FAQItem {
  question: string;
  answer: string;
}

interface FAQSection {
  title: string;
  items: FAQItem[];
}

interface FAQMatch extends FAQItem {
  section: string;
  score: number;
}

const apiKey = process.env.ANTHROPIC_API_KEY;
if (!apiKey) {
  throw new Error('ANTHROPIC_API_KEY environment variable is not set');
}

const anthropic = new Anthropic({
  apiKey: apiKey
});

// Load and parse FAQ data
const loadFAQ = (): FAQSection[] => {
  try {
    const faqPath = path.join(__dirname, 'knowledge_base', 'faq.md');
    console.log('Loading FAQ from:', faqPath);
    const content = fs.readFileSync(faqPath, 'utf8');
    console.log('FAQ content loaded, length:', content.length);
    return parseFAQ(content);
  } catch (error) {
    console.error('Error loading FAQ:', error);
    return [];
  }
};

// Parse FAQ markdown into structured data
const parseFAQ = (content: string): FAQSection[] => {
  const sections: FAQSection[] = [];
  let currentSection: string | null = null;
  let currentItems: FAQItem[] = [];

  const lines = content.split('\n');
  for (const line of lines) {
    if (line.startsWith('### ')) {
      if (currentSection) {
        sections.push({
          title: currentSection,
          items: currentItems
        });
      }
      currentSection = line.replace('### ', '').trim();
      currentItems = [];
    } else if (line.startsWith('**Q:')) {
      const question = line.replace('**Q:', '').replace('**', '').trim();
      currentItems.push({ question, answer: '' });
    } else if (line.startsWith('A:') && currentItems.length > 0) {
      currentItems[currentItems.length - 1].answer = line.replace('A:', '').trim();
    }
  }

  if (currentSection) {
    sections.push({
      title: currentSection,
      items: currentItems
    });
  }

  return sections;
};

// Find relevant FAQ entries
const findRelevantFAQ = (sections: FAQSection[], question: string): FAQMatch[] => {
  const questionLower = question.toLowerCase();
  const matches: FAQMatch[] = [];

  for (const section of sections) {
    for (const item of section.items) {
      // Count matching words
      const qWords = new Set(item.question.toLowerCase().split(/\s+/));
      const searchWords = new Set(questionLower.split(/\s+/));
      const score = [...qWords].filter(word => searchWords.has(word)).length;

      if (score > 0) {
        matches.push({
          ...item,
          section: section.title,
          score
        });
      }
    }
  }

  // Sort by relevance score
  return matches.sort((a, b) => b.score - a.score).slice(0, 2);
};

// Define types for messages and sessions
type Message = {
  role: 'user' | 'assistant';
  content: string;
};

type ChatSession = {
  messages: Message[];
  lastUpdated: Date;
};

export async function chat(message: string, sessionId?: string): Promise<{ 
  response: string; 
  sessionId: string;
  uiComponent?: {
    type: string;
    text?: string;
  };
}> {
  // Create or get existing session
  if (!sessionId || !sessions.has(sessionId)) {
    sessionId = Math.random().toString(36).substring(2);
    sessions.set(sessionId, {
      messages: [],
      lastUpdated: new Date()
    });
  }

  const session = sessions.get(sessionId)!;
  
  // Add user message to history
  session.messages.push({ role: 'user', content: message });

  // Find relevant FAQ entries
  const faqSections = loadFAQ();
  const relevantFAQ = findRelevantFAQ(faqSections, message);
  
  // Create system prompt with FAQ context if available
  let systemPrompt = `You are a helpful AI assistant for Xuno, a money transfer service specializing in transfers to Nepal. 
Your responses should be accurate and based on the provided information about Xuno's services.`;
  
  if (relevantFAQ.length > 0) {
    systemPrompt += `\n\nHere is some relevant information about Xuno:\n`;
    relevantFAQ.forEach(faq => {
      systemPrompt += `\nRegarding ${faq.section}:\nQ: ${faq.question}\nA: ${faq.answer}\n`;
    });
    systemPrompt += `\nPlease use this information to provide accurate responses about Xuno's services. 
If the user's question is directly about Xuno's services, base your response primarily on this information.
For other questions, you can provide helpful responses while staying within your role as Xuno's assistant.`;
  }
  
  // Get response from Claude with FAQ context
  const response = await anthropic.messages.create({
    model: 'claude-3-sonnet-20240229',
    max_tokens: 1000,
    system: systemPrompt,
    messages: session.messages.map(msg => ({
      role: msg.role,
      content: msg.content
    })),
    temperature: 0.7
  });

  const responseText = response.content[0].text;
  
  // Update session
  session.messages.push({ 
    role: 'assistant', 
    content: responseText 
  });
  session.lastUpdated = new Date();

  return {
    response: responseText,
    sessionId,
    uiComponent: {
      type: 'text',
      text: responseText
    }
  };
}

// Store sessions in memory
const sessions = new Map<string, ChatSession>();

// Clean up old sessions every 24 hours
setInterval(() => {
  const now = new Date();
  for (const [id, session] of sessions) {
    if (now.getTime() - session.lastUpdated.getTime() > 24 * 60 * 60 * 1000) {
      sessions.delete(id);
    }
  }
}, 24 * 60 * 60 * 1000);
