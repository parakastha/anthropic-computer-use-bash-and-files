const express = require('express');
const { spawn } = require('child_process');
const path = require('path');
const cors = require('cors');

const app = express();
const port = 3000;

app.use(cors());
app.use(express.json());

// Chatbot endpoint
app.post('/api/chat', async (req, res) => {
  const { message } = req.body;

  if (!message) {
    return res.status(400).json({
      type: 'error',
      message: 'Message is required',
    });
  }

  try {
    // Get the absolute path to the Python script
    const scriptPath = path.join(__dirname, 'scripts', 'chatbot.py');
    
    // Spawn Python process
    const python = spawn('python', [scriptPath]);
    let dataString = '';

    // Handle Python script errors
    python.stderr.on('data', (data) => {
      console.error(`Python Error: ${data}`);
    });

    // Collect data from script
    python.stdout.on('data', (data) => {
      dataString += data.toString();
    });

    // Send message to Python script
    python.stdin.write(message + '\n');
    python.stdin.end();

    // Handle completion
    python.on('close', (code) => {
      try {
        // Extract the JSON response from the output
        const outputLines = dataString.split('\n');
        const jsonResponse = outputLines.find(line => {
          try {
            JSON.parse(line);
            return true;
          } catch {
            return false;
          }
        });

        if (jsonResponse) {
          const response = JSON.parse(jsonResponse);
          res.status(200).json(response);
        } else {
          console.error('Invalid response from chatbot:', dataString);
          res.status(500).json({
            type: 'error',
            message: 'Could not get response from Xuno chatbot. Please try again.',
          });
        }
      } catch (error) {
        console.error('Error parsing chatbot response:', error);
        res.status(500).json({
          type: 'error',
          message: 'Failed to process response. Please try again.',
        });
      }
    });

    // Handle errors
    python.on('error', (err) => {
      console.error('Failed to start chatbot process:', err);
      res.status(500).json({
        type: 'error',
        message: 'Failed to connect to Xuno chatbot. Please try again.',
      });
    });

  } catch (error) {
    console.error('Internal server error:', error);
    res.status(500).json({
      type: 'error',
      message: 'Internal server error. Please try again later.',
    });
  }
});

app.listen(port, () => {
  console.log(`Server running at http://localhost:${port}`);
}); 