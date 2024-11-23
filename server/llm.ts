import Anthropic from '@anthropic-ai/sdk';

const apiKey = process.env.ANTHROPIC_API_KEY;
if (!apiKey) {
  throw new Error('ANTHROPIC_API_KEY environment variable is not set');
}

const anthropic = new Anthropic({
  apiKey: apiKey
});

// Define types for messages and sessions
type Message = { role: 'user' | 'assistant'; content: string };
type ChatSession = {
  messages: Message[];
  lastUpdated: Date;
};

// Store sessions in memory
const sessions = new Map<string, ChatSession>();

export async function chat(message: string, sessionId?: string): Promise<{ response: string; sessionId: string }> {
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
  
  // Get response from Claude
  const response = await anthropic.messages.create({
    model: 'claude-3-sonnet-20240229',
    max_tokens: 1000,
    messages: session.messages
  });
  
  // Add assistant response to history
  const assistantMessage = response.content[0].text;
  session.messages.push({ role: 'assistant', content: assistantMessage });
  
  // Update session timestamp
  session.lastUpdated = new Date();
  
  return {
    response: assistantMessage,
    sessionId
  };
}

// Clean up old sessions every 24 hours
setInterval(() => {
  const now = new Date();
  for (const [id, session] of sessions) {
    if (now.getTime() - session.lastUpdated.getTime() > 24 * 60 * 60 * 1000) {
      sessions.delete(id);
    }
  }
}, 24 * 60 * 60 * 1000);
