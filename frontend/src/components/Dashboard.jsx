import React, { useState, useEffect } from 'react';
import axios from 'axios';
import ReplyEditor from './ReplyEditor'; // Import the new component
import AiChatWindow from './AiChatWindow'; // Import the new component

const Dashboard = () => {
    const [emails, setEmails] = useState([]);
    const [chatHistory, setChatHistory] = useState([]);
    const [loading, setLoading] = useState(false);
    
    // NEW STATE: For managing the reply editor pop-up
    const [activeReply, setActiveReply] = useState(null); // e.g., { messageId, text, originalSender, originalSubject }
    
    // NEW STATE: For managing the AI chat window visibility
    const [isAiChatOpen, setIsAiChatOpen] = useState(false);


    const addToChat = (sender, message) => {
        setChatHistory(prev => [...prev, { sender, message }]);
    };
    
    useEffect(() => {
        const fetchEmails = async () => {
            addToChat('System', 'Fetching your 5 most recent emails...');
            setLoading(true);
            try {
                // IMPORTANT: The backend was updated to return `full_content`
                const response = await axios.get('http://localhost:8000/emails/recent');
                setEmails(response.data);
                addToChat('System', 'Here are your recent emails. You can generate a reply or delete them.');
            } catch (error) {
                console.error('Error fetching emails:', error);
                addToChat('Error', 'Failed to fetch emails. Please try again later.');
            }
            setLoading(false);
        };
        
        addToChat('System', 'Welcome! I am your AI Email Assistant.');
        fetchEmails();
    }, []);

    const handleGenerateReply = async (email) => {
        addToChat('System', `Generating AI reply for email from ${email.sender}...`);
        setLoading(true);
        try {
            const response = await axios.post('http://localhost:8000/emails/generate-reply', {
                content: `Subject: ${email.subject}\nSnippet: ${email.snippet}`
            });
            // NEW LOGIC: Instead of adding to chat, open the editor
            setActiveReply({
                messageId: email.id,
                text: response.data.reply,
                originalSender: email.sender,
                originalSubject: email.subject
            });
        } catch (error) {
            console.error('Error generating reply:', error);
            addToChat('Error', 'Failed to generate AI reply.');
        }
        setLoading(false);
    };
    
    // NEW FUNCTION: To handle sending the final email
    const handleSendEmail = async () => {
        if (!activeReply) return;
        
        addToChat('System', 'Sending your reply...');
        setLoading(true);
        try {
            await axios.post('http://localhost:8000/emails/send', {
                message_id: activeReply.messageId,
                reply_text: activeReply.text
            });
            addToChat('System', 'Your email has been sent successfully!');
        } catch (error) {
            console.error('Error sending email:', error);
            addToChat('Error', 'Failed to send your email.');
        }
        setLoading(false);
        setActiveReply(null); // Close the editor window
    };

    const handleDelete = async (messageId) => {
        if (!window.confirm('Are you sure you want to delete this email?')) return;
        
        addToChat('System', `Deleting email...`);
        setLoading(true);
        try {
            await axios.post('http://localhost:8000/emails/delete', { message_id: messageId });
            setEmails(prev => prev.filter(e => e.id !== messageId));
            addToChat('System', 'Email deleted successfully.');
        } catch (error) {
            console.error('Error deleting email:', error);
            addToChat('Error', 'Failed to delete email.');
        }
        setLoading(false);
    };

    return (
        <div className="dashboard">
            {/* NEW: Render the Reply Editor when there's an active reply */}
            {activeReply && (
                <ReplyEditor
                    replyData={activeReply}
                    onTextChange={(newText) => setActiveReply(prev => ({ ...prev, text: newText }))}
                    onSend={handleSendEmail}
                    onCancel={() => setActiveReply(null)}
                    isLoading={loading}
                />
            )}
            
            {/* NEW: Render the AI Chat Window when it's open */}
            {isAiChatOpen && <AiChatWindow onClose={() => setIsAiChatOpen(false)} />}
            
            {/* NEW: The floating icon to open the AI chat */}
            <button className="ai-chat-fab" onClick={() => setIsAiChatOpen(true)}>
                🤖
            </button>
            
            <div className="main-content">
                <div className="chat-window">
                    {chatHistory.map((item, index) => (
                        <div key={index} className={`chat-message ${item.sender.toLowerCase()}`}>
                            <strong>{item.sender}:</strong> {item.message}
                        </div>
                    ))}
                    {loading && emails.length === 0 && <div className="chat-message system"><em>Loading...</em></div>}
                </div>

                <div className="email-list">
                    <h3>Recent Emails</h3>
                    {loading && emails.length === 0 ? <p>Loading emails...</p> : 
                     emails.map(email => (
                        <div key={email.id} className="email-item">
                            <p><strong>From:</strong> {email.sender}</p>
                            <p><strong>Subject:</strong> {email.subject}</p>
                            <p>{email.snippet}</p>
                            <div className="email-actions">
                                <button onClick={() => handleGenerateReply(email)} disabled={loading}>Generate Reply</button>
                                <button onClick={() => handleDelete(email.id)} disabled={loading} className="delete-button">Delete</button>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};

export default Dashboard;