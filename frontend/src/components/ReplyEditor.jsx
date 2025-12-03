import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './ReplyEditor.css';

const ReplyEditor = ({ email, onSend, onClose, isOpen }) => {
  const [replyText, setReplyText] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [isSending, setIsSending] = useState(false);

  // Pre-fill with a greeting if it's a new reply
  useEffect(() => {
    if (email && !replyText) {
      const greeting = `Hi ${email.senderName || 'there'},\n\n`;
      setReplyText(greeting);
    }
  }, [email]);

  const handleGenerateReply = async () => {
    if (!email) return;
    
    setIsGenerating(true);
    try {
      // Use relative URL for Vercel deployment
      const response = await axios.post('/api/ai/generate-reply', {
        subject: email.subject,
        content: email.snippet || email.body,
        tone: 'professional' // You can make this configurable
      });
      
      setReplyText(prev => {
        // Preserve the greeting if it exists
        const hasGreeting = prev.startsWith('Hi ') || prev.startsWith('Hello ');
        return hasGreeting 
          ? prev + '\n\n' + response.data.reply 
          : response.data.reply;
      });
    } catch (error) {
      console.error('Error generating reply:', error);
      alert('Failed to generate reply. Please try again.');
    } finally {
      setIsGenerating(false);
    }
  };

  const handleSend = async (e) => {
    e.preventDefault();
    if (!replyText.trim() || !email) return;

    setIsSending(true);
    try {
      // Use relative URL for Vercel deployment
      await axios.post('/api/emails/send', {
        message_id: email.id,
        reply_text: replyText,
        in_reply_to: email.messageId
      });
      
      onSend && onSend();
      onClose();
    } catch (error) {
      console.error('Error sending reply:', error);
      alert('Failed to send reply. Please try again.');
    } finally {
      setIsSending(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="reply-editor-overlay">
      <div className="reply-editor">
        <div className="reply-header">
          <h3>Reply to {email?.senderName || email?.from || 'Email'}</h3>
          <button onClick={onClose} className="close-button">&times;</button>
        </div>
        
        <div className="email-preview">
          <strong>Subject:</strong> {email?.subject || 'No subject'}<br />
          <strong>From:</strong> {email?.from || 'Unknown sender'}<br />
          <div className="email-snippet">
            {email?.snippet || 'No content preview available...'}
          </div>
        </div>

        <div className="reply-actions">
          <button 
            onClick={handleGenerateReply} 
            disabled={isGenerating || isSending}
            className="generate-button"
          >
            {isGenerating ? 'Generating...' : 'Generate Reply'}
          </button>
        </div>

        <form onSubmit={handleSend} className="reply-form">
          <textarea
            value={replyText}
            onChange={(e) => setReplyText(e.target.value)}
            placeholder="Type your reply here..."
            disabled={isSending}
            required
          />
          <div className="form-actions">
            <button 
              type="button" 
              onClick={onClose}
              disabled={isSending}
              className="cancel-button"
            >
              Cancel
            </button>
            <button 
              type="submit" 
              disabled={!replyText.trim() || isSending || isGenerating}
              className="send-button"
            >
              {isSending ? 'Sending...' : 'Send'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default ReplyEditor;
