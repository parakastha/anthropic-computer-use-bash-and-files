import express from 'express';
import cors from 'cors';
import { chat } from './llm';
import * as dotenv from 'dotenv';
import facebookRoutes from './routes/facebook';

// Load environment variables
dotenv.config();

const app = express();
const port = process.env.PORT || 3000;
const nodeEnv = process.env.NODE_ENV || 'development';

app.use(cors());
app.use(express.json());
app.use('/api/facebook', facebookRoutes);

app.post('/chat', async (req, res) => {
  try {
    const { message, sessionId } = req.body;
    if (!message) {
      return res.status(400).json({ error: 'Message is required' });
    }
    const response = await chat(message, sessionId);
    
    // Response now includes both text and potentially a UI component
    res.json({
      response: response.response,
      sessionId: response.sessionId,
      uiComponent: response.uiComponent
    });
  } catch (error) {
    console.error('Error:', error);
    res.status(500).json({ 
      error: 'Internal server error',
      details: error instanceof Error ? error.message : String(error)
    });
  }
});

// Add tool endpoint for UI generation
app.post('/tool', async (req, res) => {
  try {
    const { message, sessionId } = req.body;
    if (!message) {
      return res.status(400).json({ error: 'Message is required' });
    }
    const response = await chat(message, sessionId);
    
    // Return the entire response including UI components
    res.json(response);
  } catch (error) {
    console.error('Error:', error);
    res.status(500).json({ 
      error: 'Internal server error',
      details: error instanceof Error ? error.message : String(error)
    });
  }
});

app.listen(port, () => {
  console.log(`Server running at http://localhost:${port}`);
  console.log('Environment:', {
    NODE_ENV: nodeEnv,
    API_KEY_SET: !!process.env.ANTHROPIC_API_KEY
  });
});
