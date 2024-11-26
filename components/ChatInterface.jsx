import React, { useState, useRef, useEffect } from 'react';
import {
  Box,
  TextField,
  Button,
  Typography,
  List,
  ListItem,
} from '@mui/material';
import FAQComponent from './FAQComponent';

// Message bubble component
const MessageBubble = ({ message, isUser }) => {
  // Helper function to format bullet points
  const formatText = (text) => {
    if (typeof text !== 'string') return text;
    return text.split('\n').map((line, i) => (
      <Typography key={i} component="div" sx={{ mb: line.startsWith('•') ? 0.5 : 1 }}>
        {line}
      </Typography>
    ));
  };

  // Handle different response types
  const renderContent = () => {
    if (typeof message === 'string') {
      return formatText(message);
    }

    switch (message.type) {
      case 'single_qa':
        return (
          <>
            <Typography variant="subtitle1" sx={{ fontWeight: 'bold', mb: 1 }}>
              {message.question}
            </Typography>
            {formatText(message.answer)}
          </>
        );
      case 'accordion':
        return <FAQComponent data={message} />;
      case 'error':
        return formatText(message.message);
      default:
        return formatText(JSON.stringify(message, null, 2));
    }
  };

  return (
    <Box
      sx={{
        display: 'flex',
        justifyContent: isUser ? 'flex-end' : 'flex-start',
        mb: 2,
      }}
    >
      <Box
        sx={{
          maxWidth: '80%',
          backgroundColor: isUser ? '#0066cc' : '#fff',
          color: isUser ? '#fff' : '#000',
          p: 2,
          borderRadius: 2,
          boxShadow: '0 1px 2px rgba(0,0,0,0.1)',
        }}
      >
        {renderContent()}
        <Typography variant="caption" sx={{ display: 'block', mt: 1, opacity: 0.7 }}>
          {new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </Typography>
      </Box>
    </Box>
  );
};

const ChatInterface = () => {
  const [messages, setMessages] = useState([
    { text: "Hi! How can I help you today?", isUser: false }
  ]);
  const [input, setInput] = useState('');
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage = input.trim();
    setInput('');
    setMessages(prev => [...prev, { text: userMessage, isUser: true }]);

    try {
      const response = await fetch('/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: userMessage }),
      });

      if (!response.ok) {
        console.error('Response not OK:', response.status, response.statusText);
        const errorText = await response.text();
        console.error('Error response:', errorText);
        throw new Error('Network response was not ok');
      }

      const data = await response.json();
      console.log('Received response:', data);
      setMessages(prev => [...prev, { 
        text: data.response, 
        isUser: false 
      }]);
    } catch (error) {
      console.error('Error in handleSend:', error);
      setMessages(prev => [...prev, {
        text: {
          type: 'error',
          message: "Sorry, I couldn't process your request. Please try again."
        },
        isUser: false
      }]);
    }
  };

  return (
    <Box sx={{ 
      height: '100vh',
      display: 'flex',
      flexDirection: 'column',
      bgcolor: '#f5f5f5'
    }}>
      {/* Header */}
      <Box sx={{ 
        p: 2, 
        bgcolor: '#fff',
        borderBottom: '1px solid #e0e0e0'
      }}>
        <Typography variant="h6" align="center">
          Xuno Chat
        </Typography>
      </Box>

      {/* Messages */}
      <Box sx={{ 
        flex: 1, 
        overflowY: 'auto', 
        p: 2,
      }}>
        {messages.map((msg, index) => (
          <MessageBubble
            key={index}
            message={msg.text}
            isUser={msg.isUser}
          />
        ))}
        <div ref={messagesEndRef} />
      </Box>

      {/* Input area */}
      <Box
        component="form"
        onSubmit={handleSend}
        sx={{
          p: 2,
          bgcolor: '#fff',
          borderTop: '1px solid #e0e0e0',
        }}
      >
        <Box sx={{ display: 'flex', gap: 1 }}>
          <TextField
            fullWidth
            variant="outlined"
            placeholder="Type your message..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            sx={{
              '& .MuiOutlinedInput-root': {
                borderRadius: 3,
              }
            }}
          />
          <Button
            type="submit"
            variant="contained"
            disabled={!input.trim()}
            sx={{
              borderRadius: 3,
              minWidth: 100,
              bgcolor: '#0066cc',
              '&:hover': {
                bgcolor: '#0052a3'
              }
            }}
          >
            Send
          </Button>
        </Box>
      </Box>
    </Box>
  );
};

export default ChatInterface; 