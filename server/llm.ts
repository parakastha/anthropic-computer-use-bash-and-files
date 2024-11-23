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
    system: "You are a helpful AI assistant that generates UI components. Always start your response with the component type in brackets, like [text], [starRating], [colorPicker], or [contactForm], followed by your explanation.",
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
