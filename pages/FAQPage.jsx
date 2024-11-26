import React, { useState } from 'react';
import {
  Container,
  TextField,
  Button,
  Box,
  CircularProgress,
} from '@mui/material';
import FAQComponent from '../components/FAQComponent';

const FAQPage = () => {
  const [question, setQuestion] = useState('');
  const [response, setResponse] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const res = await fetch('/api/faq', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ question }),
      });

      const data = await res.json();
      setResponse(data);
    } catch (error) {
      setResponse({
        type: 'error',
        message: 'Failed to fetch response. Please try again.',
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="md">
      <Box py={4}>
        <form onSubmit={handleSubmit}>
          <Box display="flex" gap={2} mb={4}>
            <TextField
              fullWidth
              variant="outlined"
              placeholder="Ask a question or type 'faq' to see all questions"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
            />
            <Button
              type="submit"
              variant="contained"
              color="primary"
              disabled={loading || !question.trim()}
            >
              {loading ? <CircularProgress size={24} /> : 'Ask'}
            </Button>
          </Box>
        </form>

        {response && <FAQComponent data={response} />}
      </Box>
    </Container>
  );
};

export default FAQPage; 