import React, { useState } from 'react';
import { motion } from 'framer-motion';
import axios from 'axios';
import './App.css';

function App() {
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const [miaContext, setMiaContext] = useState('');
  const [lunaContext, setLunaContext] = useState('');
  const [notification, setNotification] = useState('');

  const handleContextSubmit = async () => {
    if (!miaContext.trim() && !lunaContext.trim()) return;

    setIsLoading(true);
    setNotification('');

    try {
      await axios.post('http://127.0.0.1:8000/add_context', {
        mia_context: miaContext,
        luna_context: lunaContext
      });
      setNotification('Context updated successfully!');
    } catch (error) {
      setNotification('Failed to update context. Please try again.');
      console.error('Error updating context:', error);
    } finally {
      setIsLoading(false);
      setTimeout(() => setNotification(''), 3000); // Clear notification after 3 seconds
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!question.trim()) return;

    setIsLoading(true);
    setAnswer('');
    setIsTyping(true);

    try {
      const response = await axios.post('http://127.0.0.1:8000/ask', {
        question: question
      });
      
      // Simulate typing effect
      const text = response.data.answer;
      let displayText = '';
      for (let i = 0; i < text.length; i++) {
        await new Promise(resolve => setTimeout(resolve, 10));
        displayText += text[i];
        setAnswer(displayText);
      }
    } catch (error) {
      setAnswer('Sorry, I\'m having trouble connecting to the pediatrician right now. Please try again later.');
      console.error('Error:', error);
    } finally {
      setIsLoading(false);
      setIsTyping(false);
    }
  };

  return (
    <div className="App">
      <div className="container">
        <motion.div
          initial={{ opacity: 0, y: -50 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="header"
        >
          <h1>AI Pediatrician</h1>
          <p>Ask me anything about Luna and Mia!</p>
        </motion.div>

        <div className="context-container">
          <motion.div className="context-box" initial={{ opacity: 0, x: -50 }} animate={{ opacity: 1, x: 0 }} transition={{ duration: 0.8, delay: 0.1 }}>
            <label htmlFor="mia-context">Add Context for Mia</label>
            <textarea
              id="mia-context"
              value={miaContext}
              onChange={(e) => setMiaContext(e.target.value)}
              placeholder="e.g., Mia's age, weight, recent symptoms..."
              className="context-input"
              disabled={isLoading}
            />
          </motion.div>
          <motion.div className="context-box" initial={{ opacity: 0, x: 50 }} animate={{ opacity: 1, x: 0 }} transition={{ duration: 0.8, delay: 0.1 }}>
            <label htmlFor="luna-context">Add Context for Luna</label>
            <textarea
              id="luna-context"
              value={lunaContext}
              onChange={(e) => setLunaContext(e.target.value)}
              placeholder="e.g., Luna's age, weight, recent symptoms..."
              className="context-input"
              disabled={isLoading}
            />
          </motion.div>
        </div>

        <div className="context-submit-container">
          <motion.button
            onClick={handleContextSubmit}
            className="context-submit-button"
            disabled={isLoading || (!miaContext.trim() && !lunaContext.trim())}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            Update Context
          </motion.button>
        </div>
        
        {notification && <div className="notification">{notification}</div>}

        <motion.form
          initial={{ opacity: 0, y: 50 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.2 }}
          onSubmit={handleSubmit}
          className="question-form"
        >
          <div className="input-container">
            <input
              type="text"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="Ask me about your baby's development, feeding, sleep, or anything else..."
              className="question-input"
              disabled={isLoading}
            />
            <motion.button
              type="submit"
              className="ask-button"
              disabled={isLoading || !question.trim()}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              {isLoading ? '🤔 Thinking...' : 'Ask Doctor'}
            </motion.button>
          </div>
        </motion.form>

        {answer && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="answer-container"
          >
            <div className="answer-box">
              <h3>AI Pediatrician says:</h3>
              <p className="answer-text">
                {answer}
                {isTyping && <span className="typing-indicator">|</span>}
              </p>
            </div>
          </motion.div>
        )}
      </div>
    </div>
  );
}

export default App;
