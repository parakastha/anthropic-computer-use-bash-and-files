import path from 'path';
import fs from 'fs';

// Load and parse FAQ data
const loadFAQ = () => {
  try {
    const faqPath = path.join(process.cwd(), 'knowledge_base', 'faq.md');
    console.log('Loading FAQ from:', faqPath);
    const content = fs.readFileSync(faqPath, 'utf8');
    console.log('FAQ content loaded, length:', content.length);
    const sections = parseFAQ(content);
    console.log('Parsed sections:', sections.length);
    return sections;
  } catch (error) {
    console.error('Error loading FAQ:', error);
    return [];
  }
};

// Parse FAQ markdown into structured data
const parseFAQ = (content) => {
  const sections = [];
  let currentSection = null;
  let currentItems = [];

  const lines = content.split('\n');
  console.log('Total lines to parse:', lines.length);

  for (const line of lines) {
    if (line.startsWith('### ')) {
      if (currentSection) {
        console.log(`Adding section: ${currentSection} with ${currentItems.length} items`);
        sections.push({
          title: currentSection,
          items: currentItems
        });
      }
      currentSection = line.replace('### ', '').trim();
      currentItems = [];
    } else if (line.startsWith('**Q:')) {
      const question = line.replace('**Q:', '').replace('**', '').trim();
      const answer = '';
      currentItems.push({ question, answer });
    } else if (line.startsWith('A:') && currentItems.length > 0) {
      currentItems[currentItems.length - 1].answer = line.replace('A:', '').trim();
    }
  }

  if (currentSection) {
    console.log(`Adding final section: ${currentSection} with ${currentItems.length} items`);
    sections.push({
      title: currentSection,
      items: currentItems
    });
  }

  return sections;
};

// Find best matching Q&A
const findBestMatch = (sections, question) => {
  const questionLower = question.toLowerCase();
  let bestMatch = null;
  let bestScore = 0;

  console.log('Searching for:', questionLower);

  for (const section of sections) {
    console.log(`Searching in section: ${section.title}`);
    for (const item of section.items) {
      // Count matching words
      const qWords = new Set(item.question.toLowerCase().split(/\s+/));
      const searchWords = new Set(questionLower.split(/\s+/));
      const score = [...qWords].filter(word => searchWords.has(word)).length;

      console.log(`Question: "${item.question}", Score: ${score}`);

      if (score > bestScore) {
        bestScore = score;
        bestMatch = item;
      }
    }
  }

  console.log('Best match found:', bestMatch?.question, 'with score:', bestScore);
  return bestMatch;
};

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ message: 'Method not allowed' });
  }

  const { message } = req.body;
  console.log('Received message:', message);

  if (!message) {
    return res.status(400).json({
      type: 'error',
      message: 'Message is required',
    });
  }

  try {
    const faqSections = loadFAQ();
    console.log('FAQ sections loaded:', faqSections.length);

    // Handle FAQ request
    if (message.toLowerCase().includes('faq')) {
      console.log('Returning full FAQ');
      return res.status(200).json({
        type: 'accordion',
        sections: faqSections
      });
    }

    // Find best matching question
    const match = findBestMatch(faqSections, message);
    if (match) {
      console.log('Found match:', match.question);
      return res.status(200).json({
        type: 'single_qa',
        question: match.question,
        answer: match.answer
      });
    }

    console.log('No match found');
    // No match found
    return res.status(200).json({
      type: 'error',
      message: "I couldn't find a specific answer to your question. You can:\n• Ask about our fees and rates\n• Learn about the transfer process\n• Check supported countries\n• Type 'faq' to see all available topics"
    });

  } catch (error) {
    console.error('Error processing request:', error);
    return res.status(500).json({
      type: 'error',
      message: 'Internal server error. Please try again later.'
    });
  }
} 