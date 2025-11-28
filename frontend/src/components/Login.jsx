import React, { useState, useEffect } from 'react';
import { useGoogleLogin, googleLogout } from '@react-oauth/google';
import axios from 'axios';

const Login = ({ onLoginSuccess }) => {
    const [error, setError] = useState(null);
    const [isLoading, setIsLoading] = useState(false);

    // Set up the login flow - using 'implicit' flow with access token instead of code flow
    const login = useGoogleLogin({
        onSuccess: async (response) => {
            try {
                console.log("[Frontend] Login successful, response:", response);
                setIsLoading(true);
                
                // Send the access token directly to the backend
                const result = await axios.post('http://localhost:8000/auth/google', {
                    access_token: response.access_token,
                    token_type: response.token_type,
                    expires_in: response.expires_in
                });
                
                if (result.data.status === 'success') {
                    console.log("[Frontend] Authentication successful!");
                    setError(null);
                    onLoginSuccess(); // Notify parent component
                }
            } catch (error) {
                console.error("[Frontend] Authentication failed:", error.response?.data || error.message);
                setError(error.response?.data?.detail || "Authentication failed. Please try again.");
                setIsLoading(false);
            }
        },
        onError: (error) => {
            console.error("[Frontend] Login error:", error);
            setError("Failed to initiate login. Please try again.");
        },
        // Use implicit/token flow instead of authorization code flow
        flow: 'implicit',
        scope: 'https://www.googleapis.com/auth/gmail.readonly https://www.googleapis.com/auth/gmail.send https://www.googleapis.com/auth/gmail.modify',
    });

    return (
        <div className="login-container">
            <h2>Welcome</h2>
            <p>Please sign in with Google to continue</p>
            {error && <div className="error-message">{error}</div>}
            <button 
                onClick={() => login()} 
                className="login-button"
                disabled={isLoading}
            >
                {isLoading ? 'Signing in...' : 'Sign in with Google'}
            </button>
        </div>
    );
};

export default Login;
