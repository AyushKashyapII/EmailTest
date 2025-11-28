import React from 'react';
import './ReplyEditor.css'; // We will create this CSS file next

const ReplyEditor = ({ replyData, onTextChange, onSend, onCancel, isLoading }) => {
    return (
        <div className="reply-editor-overlay">
            <div className="reply-editor">
                <h3>Review and Send Reply</h3>
                <p>Replying to: <strong>{replyData.originalSender}</strong></p>
                <p>Subject: <strong>{replyData.originalSubject}</strong></p>
                <textarea
                    value={replyData.text}
                    onChange={(e) => onTextChange(e.target.value)}
                    rows="10"
                    disabled={isLoading}
                />
                <div className="reply-editor-actions">
                    <button onClick={onCancel} disabled={isLoading} className="cancel-button">
                        Cancel
                    </button>
                    <button onClick={onSend} disabled={isLoading} className="send-button">
                        {isLoading ? 'Sending...' : 'Send Email'}
                    </button>
                </div>
            </div>
        </div>
    );
};

export default ReplyEditor;