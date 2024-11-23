import Anthropic from '@anthropic-ai/sdk';

const apiKey = process.env.ANTHROPIC_API_KEY;
if (!apiKey) {
  throw new Error('ANTHROPIC_API_KEY environment variable is not set');
}

const anthropic = new Anthropic({
  apiKey: apiKey
});

// Define types for UI generation tool
type GenUITool = {
  component_type: 'text' | 'starRating' | 'colorPicker' | 'contactForm';
  textResponse?: string;
};

// Define types for Claude API response
type ContentType = 'text' | 'tool_calls';

type TextContent = {
  type: 'text';
  text: string;
};

type ToolCallFunction = {
  name: string;
  arguments: string;
};

type ToolCall = {
  type: 'function';
  function: ToolCallFunction;
};

type ToolCallsContent = {
  type: 'tool_calls';
  tool_calls: ToolCall[];
};

type MessageContent = TextContent | ToolCallsContent;

// Define types for messages and sessions
type Message = {
  role: 'user' | 'assistant';
  content: string;
};

type ChatSession = {
  messages: Message[];
  lastUpdated: Date;
};

// Store sessions in memory
const sessions = new Map<string, ChatSession>();

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
  
  // Get response from Claude
  const response = await anthropic.messages.create({
    model: 'claude-3-sonnet-20240229',
    max_tokens: 1000,
    system: `You are a helpful AI assistant that generates UI components based on user requests. Choose the most appropriate component type based on these rules:

1. Use [text] for general responses, explanations, or when displaying text content
2. Use [starRating] when the user wants to rate something or provide a rating interface
3. Use [colorPicker] when the user wants to select or work with colors
4. Use [contactForm] when the user needs to submit contact information or fill out a form

Always start your response with one of these component types in brackets, followed by your explanation. For example:
[text] Here's the information you requested...
[starRating] You can rate this item from 1 to 5 stars...
[colorPicker] Choose your preferred color...
[contactForm] Please fill out your contact details...`,
    messages: session.messages.map(msg => ({
      role: msg.role,
      content: msg.content
    })),
    temperature: 0.7
  });

  // Get the text response
  const textContent = response.content[0];
  const assistantMessage = textContent.text;

  // Try to parse component type from the response
  let uiComponent;
  const componentTypeMatch = assistantMessage.match(/^\[(.*?)\]/);
  if (componentTypeMatch) {
    const componentType = componentTypeMatch[1];
    uiComponent = {
      type: componentType,
      text: assistantMessage.replace(/^\[.*?\]\s*/, '').trim()
    };
  }

  // Add assistant response to history
  session.messages.push({ role: 'assistant', content: assistantMessage });
  
  // Update session timestamp
  session.lastUpdated = new Date();
  
  return {
    response: assistantMessage,
    sessionId,
    uiComponent
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
