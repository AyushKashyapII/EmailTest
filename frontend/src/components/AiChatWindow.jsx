import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import './AiChatWindow.css'; // We will create this CSS file next

const AiChatWindow = ({ onClose }) => {
    const [messages, setMessages] = useState([
        { sender: 'AI', text: 'Hello! How can I help you draft an email today?' }
    ]);
    const [userInput, setUserInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const chatBodyRef = useRef(null);

    // Auto-scroll to the bottom
    useEffect(() => {
        if (chatBodyRef.current) {
            chatBodyRef.current.scrollTop = chatBodyRef.current.scrollHeight;
        }
    }, [messages]);

    const handleSendMessage = async (e) => {
        e.preventDefault();
        if (!userInput.trim() || isLoading) return;

        const newMessages = [...messages, { sender: 'User', text: userInput }];
        setMessages(newMessages);
        setUserInput('');
        setIsLoading(true);

        try {
            const response = await axios.post('http://localhost:8000/ai/draft', {
                prompt: userInput
            });
            setMessages(prev => [...prev, { sender: 'AI', text: response.data.draft }]);
        } catch (error) {
            console.error('Error with AI draft:', error);
            setMessages(prev => [...prev, { sender: 'AI', text: 'Sorry, I encountered an error. Please try again.' }]);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="ai-chat-overlay">
            <div className="ai-chat-window">
                <div className="ai-chat-header">
                    <h3>AI Assistant</h3>
                    <button onClick={onClose} className="close-button">&times;</button>
                </div>
                <div className="ai-chat-body" ref={chatBodyRef}>
                    {messages.map((msg, index) => (
                        <div key={index} className={`message ${msg.sender.toLowerCase()}`}>
                            <p>{msg.text}</p>
                        </div>
                    ))}
                    {isLoading && <div className="message ai"><p><i>Typing...</i></p></div>}
                </div>
                <form className="ai-chat-footer" onSubmit={handleSendMessage}>
                    <input
                        type="text"
                        value={userInput}
                        onChange={(e) => setUserInput(e.target.value)}
                        placeholder="e.g., Draft an email to my team..."
                        disabled={isLoading}
                    />
                    <button type="submit" disabled={isLoading}>Send</button>
                </form>
            </div>
        </div>
    );
};

export default AiChatWindow;