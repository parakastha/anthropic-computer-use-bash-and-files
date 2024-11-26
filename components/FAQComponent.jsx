import React, { useState } from 'react';
import {
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Typography,
  Box,
  Container,
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';

// Single Q&A Component
const QAItem = ({ question, answer }) => {
  return (
    <Accordion>
      <AccordionSummary
        expandIcon={<ExpandMoreIcon />}
        aria-controls={`${question}-content`}
        id={`${question}-header`}
      >
        <Typography fontWeight="medium">{question}</Typography>
      </AccordionSummary>
      <AccordionDetails>
        <Typography>{answer}</Typography>
      </AccordionDetails>
    </Accordion>
  );
};

// FAQ Section Component
const FAQSection = ({ title, items }) => {
  return (
    <Box mb={3}>
      <Typography variant="h6" gutterBottom color="primary">
        {title}
      </Typography>
      {items.map((item, index) => (
        <QAItem key={index} {...item} />
      ))}
    </Box>
  );
};

// Main FAQ Component
const FAQComponent = ({ data }) => {
  if (!data) return null;

  // Handle different response types
  switch (data.type) {
    case 'accordion':
      return (
        <Container maxWidth="md">
          <Box py={4}>
            <Typography variant="h4" gutterBottom align="center">
              Frequently Asked Questions
            </Typography>
            {data.sections.map((section, index) => (
              <FAQSection key={index} {...section} />
            ))}
          </Box>
        </Container>
      );

    case 'single_qa':
      return (
        <Container maxWidth="md">
          <Box py={4}>
            <QAItem question={data.question} answer={data.answer} />
          </Box>
        </Container>
      );

    case 'error':
      return (
        <Container maxWidth="md">
          <Box py={4}>
            <Typography color="error" align="center">
              {data.message}
            </Typography>
          </Box>
        </Container>
      );

    default:
      return null;
  }
};

export default FAQComponent; 