import { spawn } from 'child_process';

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ message: 'Method not allowed' });
  }

  const { question } = req.body;

  if (!question) {
    return res.status(400).json({
      type: 'error',
      message: 'Question is required',
    });
  }

  try {
    // Spawn Python process
    const python = spawn('python', ['chatbot.py']);
    let dataString = '';

    // Collect data from script
    python.stdout.on('data', (data) => {
      dataString += data.toString();
    });

    // Send question to Python script
    python.stdin.write(question + '\n');
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
          res.status(500).json({
            type: 'error',
            message: 'Invalid response from chatbot',
          });
        }
      } catch (error) {
        res.status(500).json({
          type: 'error',
          message: 'Failed to parse chatbot response',
        });
      }
    });

    // Handle errors
    python.on('error', (err) => {
      res.status(500).json({
        type: 'error',
        message: 'Failed to start chatbot process',
      });
    });

  } catch (error) {
    res.status(500).json({
      type: 'error',
      message: 'Internal server error',
    });
  }
} 