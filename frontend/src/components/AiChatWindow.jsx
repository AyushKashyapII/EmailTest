import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import './AiChatWindow.css';

const AiChatWindow = ({ onClose, emailContext }) => {
  const [messages, setMessages] = useState([]);
  const [userInput, setUserInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const chatBodyRef = useRef(null);

  // Initialize with welcome message
  useEffect(() => {
    setMessages([{
      sender: 'ai',
      text: 'Hello! I\'m your email assistant. How can I help you with your emails today?'
    }]);
  }, []);

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!userInput.trim()) return;

    // Add user message to chat
    const userMessage = { sender: 'user', text: userInput };
    setMessages(prev => [...prev, userMessage]);
    setUserInput('');
    setIsLoading(true);

    try {
      // Use relative URL for Vercel deployment
      const response = await axios.post('/api/ai/chat', {
        message: userInput,
        context: emailContext
      });

      // Add AI response to chat
      setMessages(prev => [...prev, {
        sender: 'ai',
        text: response.data.response
      }]);
    } catch (error) {
      console.error('Error sending message:', error);
      setMessages(prev => [...prev, {
        sender: 'ai',
        text: 'Sorry, I encountered an error. Please try again.'
      }]);
    } finally {
      setIsLoading(false);
      // Scroll to bottom of chat
      if (chatBodyRef.current) {
        chatBodyRef.current.scrollTop = chatBodyRef.current.scrollHeight;
      }
    }
  };

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    if (chatBodyRef.current) {
      chatBodyRef.current.scrollTop = chatBodyRef.current.scrollHeight;
    }
  }, [messages]);

  return (
    <div className="ai-chat-window">
      <div className="ai-chat-header">
        <h3>AI Email Assistant</h3>
        <button onClick={onClose} className="close-button">&times;</button>
      </div>
      <div className="ai-chat-body" ref={chatBodyRef}>
        {messages.map((msg, index) => (
          <div key={index} className={`message ${msg.sender}`}>
            <div className={`message-content ${msg.sender}`}>
              {msg.text}
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="message ai">
            <div className="typing-indicator">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        )}
      </div>
      <form className="ai-chat-footer" onSubmit={handleSendMessage}>
        <input
          type="text"
          value={userInput}
          onChange={(e) => setUserInput(e.target.value)}
          placeholder="Type your message here..."
          disabled={isLoading}
        />
        <button type="submit" disabled={isLoading || !userInput.trim()}>
          {isLoading ? 'Sending...' : 'Send'}
        </button>
      </form>
    </div>
  );
};

export default AiChatWindow;
