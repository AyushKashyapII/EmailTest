import React, { useState } from 'react';
import { GoogleOAuthProvider } from '@react-oauth/google';
import Login from './components/Login';
import Dashboard from './components/Dashboard';
import './App.css';

const App = () => {
    const [isAuthenticated, setIsAuthenticated] = useState(false);

    // Get your Client ID from the Google Cloud Console
    const googleClientId = "360839713422-sn3v0lqjege9c0bv105uqaj983bga0db.apps.googleusercontent.com";

    return (
        <GoogleOAuthProvider clientId={googleClientId}>
            <div className="App">
                <header className="App-header">
                    <h1>Constructure AI - Email Assistant</h1>
                </header>
                <main>
                    {!isAuthenticated ? (
                        <Login onLoginSuccess={() => setIsAuthenticated(true)} />
                    ) : (
                        <Dashboard />
                    )}
                </main>
            </div>
        </GoogleOAuthProvider>
    );
};

export default App;
