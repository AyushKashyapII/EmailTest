import React, { useState, useEffect } from 'react';
import axios from 'axios';
import ReplyEditor from './ReplyEditor';
import AiChatWindow from './AiChatWindow';

// Main Dashboard Component
const Dashboard = () => {
    const [emails, setEmails] = useState([]);
    const [loading, setLoading] = useState(false);
    
    // State for the main notification/action log window
    const [actionLog, setActionLog] = useState([]);
    const [userInput, setUserInput] = useState(""); // For the new command input

    // State for the pop-up reply editor
    const [activeReply, setActiveReply] = useState(null);
    
    // State for the pop-up AI drafting chat window
    const [isAiChatOpen, setIsAiChatOpen] = useState(false);

    // Helper function to add messages to the action log
    const addToLog = (sender, message) => {
        setActionLog(prev => [...prev, { sender, message }]);
    };

    // Initial effect to fetch emails when the component loads
    useEffect(() => {
        const fetchEmails = async () => {
            addToLog('System', 'Fetching your 5 most recent emails...');
            setLoading(true);
            try {
                const response = await axios.get('http://localhost:8000/emails/recent');
                setEmails(response.data);
                addToLog('System', 'Here are your recent emails. You can ask me to "delete the email from [sender]" or use the buttons below.');
            } catch (error) {
                console.error('Error fetching emails:', error);
                addToLog('Error', 'Failed to fetch emails. Please try again later.');
            }
            setLoading(false);
        };
        
        addToLog('System', 'Welcome! I am your AI Email Assistant.');
        fetchEmails();
    }, []);

    // --- Core Action Handlers ---

    const handleGenerateReply = async (email) => {
        addToLog('System', `Generating AI reply for email from ${email.sender}...`);
        setLoading(true);
        try {
            const response = await axios.post('http://localhost:8000/emails/generate-reply', {
                content: `Subject: ${email.subject}\nSnippet: ${email.snippet}`
            });
            // Open the reply editor with the AI's suggestion
            setActiveReply({
                messageId: email.id,
                text: response.data.reply,
                originalSender: email.sender,
                originalSubject: `Re: ${email.subject}`
            });
        } catch (error) {
            console.error('Error generating reply:', error);
            addToLog('Error', 'Failed to generate AI reply.');
        }
        setLoading(false);
    };
    
    const handleSendEmail = async () => {
        if (!activeReply) return;
        
        addToLog('System', 'Sending your reply...');
        setLoading(true);
        try {
            await axios.post('http://localhost:8000/emails/send', {
                message_id: activeReply.messageId,
                reply_text: activeReply.text
            });
            addToLog('System', 'Your email has been sent successfully!');
        } catch (error) {
            console.error('Error sending email:', error);
            addToLog('Error', 'Failed to send your email.');
        }
        setLoading(false);
        setActiveReply(null); // Close the editor window
    };

    const handleDelete = async (messageId) => {
        if (!window.confirm('Are you sure you want to delete this email?')) return;
        
        addToLog('System', `Deleting email...`);
        setLoading(true);
        try {
            await axios.post('http://localhost:8000/emails/delete', { message_id: messageId });
            // Update UI to reflect the deletion
            setEmails(prev => prev.filter(e => e.id !== messageId));
            addToLog('System', 'Email deleted successfully.');
        } catch (error) {
            console.error('Error deleting email:', error);
            addToLog('Error', 'Failed to delete email.');
        }
        setLoading(false);
    };

    // --- NEW Chatbot Command Handler ---
    const handleSendCommand = async (e) => {
        e.preventDefault();
        if (!userInput.trim() || loading) return;

        const commandToSend = userInput;
        addToLog('You', commandToSend);
        setUserInput("");
        setLoading(true);

        try {
            const response = await axios.post('http://localhost:8000/chatbot/command', {
                command: commandToSend
            });
            addToLog('Assistant', response.data.reply);
            
            // If the command was a successful deletion, we should refresh the email list
            if (response.data.reply.toLowerCase().includes('deleted')) {
                 const emailResponse = await axios.get('http://localhost:8000/emails/recent');
                 setEmails(emailResponse.data);
            }
        } catch (error) {
            console.error('Error sending command:', error);
            addToLog('Error', 'There was an error processing your command.');
        }
        setLoading(false);
    };

    return (
        <div className="dashboard">
            {/* Pop-up Modals */}
            {activeReply && (
                <ReplyEditor
                    replyData={activeReply}
                    onTextChange={(newText) => setActiveReply(prev => ({ ...prev, text: newText }))}
                    onSend={handleSendEmail}
                    onCancel={() => setActiveReply(null)}
                    isLoading={loading}
                />
            )}
            
            {isAiChatOpen && <AiChatWindow onClose={() => setIsAiChatOpen(false)} />}
            
            {/* <button className="ai-chat-fab" onClick={() => setIsAiChatOpen(true)} title="Open AI Draft Assistant">
                🤖
            </button> */}
            
            {/* Main Content Layout */}
            <div className="main-content">
                <div className="chat-container">
                    <div className="chat-window">
                        {actionLog.map((item, index) => (
                            <div key={index} className={`chat-message ${item.sender.toLowerCase().replace(/\s+/g, '-')}`}>
                                <strong>{item.sender}:</strong> {item.message}
                            </div>
                        ))}
                         {loading && <div className="chat-message system"><em>Processing...</em></div>}
                    </div>
                    <form className="chat-input-form" onSubmit={handleSendCommand}>
                        <input
                            type="text"
                            value={userInput}
                            onChange={(e) => setUserInput(e.target.value)}
                            placeholder="Try 'delete the email from Google'"
                            disabled={loading}
                        />
                        <button type="submit" disabled={loading}>Send</button>
                    </form>
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