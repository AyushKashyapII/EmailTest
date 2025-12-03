import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './Dashboard.css';
import AiChatWindow from './AiChatWindow';
import ReplyEditor from './ReplyEditor';

const Dashboard = () => {
    const [emails, setEmails] = useState([]);
    const [loading, setLoading] = useState(false);
    const [actionLog, setActionLog] = useState([]);
    const [showChat, setShowChat] = useState(false);
    const [showReplyEditor, setShowReplyEditor] = useState(false);
    const [selectedEmail, setSelectedEmail] = useState(null);

    const addToLog = (sender, message) => {
        console.log(`[${sender}] ${message}`);
        setActionLog(prev => [...prev, { sender, message }]);
    };

    // Initial effect to fetch emails when the component loads
    useEffect(() => {
        const fetchEmails = async () => {
            addToLog('System', 'Fetching your 5 most recent emails...');
            setLoading(true);
            try {
                const response = await axios.get('/api/emails/recent');
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

    const handleReplyClick = (email) => {
        setSelectedEmail(email);
        setShowReplyEditor(true);
    };

    const handleSendEmail = async (replyData) => {
        try {
            await axios.post('/api/emails/send', replyData);
            addToLog('System', 'Reply sent successfully!');
            return true;
        } catch (error) {
            console.error('Error sending email:', error);
            addToLog('Error', 'Failed to send reply. Please try again.');
            return false;
        }
    };

    const handleDelete = async (messageId) => {
        try {
            await axios.post('/api/emails/delete', { message_id: messageId });
            setEmails(prev => prev.filter(email => email.id !== messageId));
            addToLog('System', 'Email deleted successfully.');
        } catch (error) {
            console.error('Error deleting email:', error);
            addToLog('Error', 'Failed to delete email. Please try again.');
        }
    };

    return (
        <div className="dashboard">
            <div className="email-list">
                <h2>Recent Emails</h2>
                {loading ? (
                    <p>Loading emails...</p>
                ) : (
                    <ul>
                        {emails.map(email => (
                            <li key={email.id} className="email-item">
                                <div className="email-header">
                                    <span className="sender">{email.sender || 'Unknown Sender'}</span>
                                    <span className="date">
                                        {new Date(email.date).toLocaleString()}
                                    </span>
                                </div>
                                <div className="email-subject">{email.subject || '(No subject)'}</div>
                                <div className="email-snippet">{email.snippet || 'No preview available'}</div>
                                <div className="email-actions">
                                    <button 
                                        onClick={() => handleReplyClick(email)}
                                        className="action-button reply-button"
                                    >
                                        Reply
                                    </button>
                                    <button 
                                        onClick={() => handleDelete(email.id)}
                                        className="action-button delete-button"
                                    >
                                        Delete
                                    </button>
                                </div>
                            </li>
                        ))}
                    </ul>
                )}
            </div>

            <div className="action-log">
                <h2>Action Log</h2>
                <div className="log-entries">
                    {actionLog.map((entry, index) => (
                        <div key={index} className={`log-entry ${entry.sender.toLowerCase()}`}>
                            <span className="log-sender">[{entry.sender}]:</span>
                            <span className="log-message"> {entry.message}</span>
                        </div>
                    ))}
                </div>
            </div>

            {/* AI Chat Window */}
            <button 
                onClick={() => setShowChat(!showChat)} 
                className="ai-assistant-button"
            >
                {showChat ? 'Hide Assistant' : 'AI Assistant'}
            </button>
            
            {showChat && (
                <AiChatWindow 
                    onClose={() => setShowChat(false)} 
                    addToLog={addToLog}
                />
            )}
            
            {showReplyEditor && selectedEmail && (
                <ReplyEditor 
                    email={selectedEmail} 
                    onSend={handleSendEmail} 
                    onClose={() => {
                        setShowReplyEditor(false);
                        setSelectedEmail(null);
                    }} 
                    isOpen={showReplyEditor}
                />
            )}
        </div>
    );
};

export default Dashboard;
