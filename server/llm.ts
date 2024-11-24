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
    system: `You are a helpful AI assistant that generates UI components based on user requests. For each response, you must specify the component type in a JSON format at the end of your message, like this:

{
  "component": "text" | "starRating" | "colorPicker" | "contactForm"
}

Choose components based on these rules:
1. Use "text" for general responses and explanations
2. Use "starRating" when the user wants to rate something
3. Use "colorPicker" when the user wants to select colors
4. Use "contactForm" when the user asks about contact information or forms

First provide your natural response, then include the JSON component specification at the end.
Example:
I'd be happy to help you get in touch! Please fill out the contact form below.
{"component": "contactForm"}`,
    messages: session.messages.map(msg => ({
      role: msg.role,
      content: msg.content
    })),
    temperature: 0.7
  });

  // Extract the component type from the response
  const responseText = response.content[0].text;
  let componentType = 'text';
  let cleanResponse = responseText;

  try {
    const match = responseText.match(/\{[\s\n]*"component"[\s\n]*:[\s\n]*"([^"]+)"[\s\n]*\}/);
    if (match) {
      componentType = match[1];
      cleanResponse = responseText.replace(/\{[\s\n]*"component"[\s\n]*:[\s\n]*"[^"]+"[\s\n]*\}/, '').trim();
    }
  } catch (error) {
    console.error('Error parsing component type:', error);
  }

  // Update session
  session.messages.push({ 
    role: 'assistant', 
    content: cleanResponse 
  });
  session.lastUpdated = new Date();

  return {
    response: cleanResponse,
    sessionId,
    uiComponent: {
      type: componentType,
      text: cleanResponse
    }
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
