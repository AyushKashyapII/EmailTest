AI-Powered Email Assistant
AI-Powered Email Assistant is a mini-platform built for the Constructure AI Applicant Challenge. It demonstrates a production-style workflow that combines secure authentication, a conversational AI interface, and intelligent email automation.

Users can securely log in with Google, view recent emails, and use natural language to read, summarize, reply to, and delete emails through an AI-powered chatbot.

✨ Core Features
Secure Google OAuth 2.0 Authentication

Sign in with your Google account using OAuth 2.0.

Requests permissions to read, modify, and send emails on your behalf.

Conversational AI Chatbot

Central chatbot interface that understands natural language commands.

Goes beyond simple conditionals to provide a more intuitive, conversational experience.

Advanced Intent Recognition

Backend parses user messages to detect intents such as:

fetch_emails

generate_reply

delete_email

Extracts key entities like sender names, subject keywords, or positions such as “first”, “second”, or “last”.

Conversation Memory & Context Awareness

Remembers context across turns in a session.

After fetching emails, users can say things like “delete the second one” or “draft a reply to the latest email” and the assistant resolves those references correctly.

Intelligent Email Automation

Read & Summarize

Fetches recent emails from the inbox (or filtered by sender).

Generates concise summaries with sender, subject, and key content.

AI-Powered Replies

Creates context-aware, professional reply drafts for any email with a single command.

Natural Language Deletion

Deletes emails by sender or by position in the last fetched list, e.g. “delete the email from Amazon”.

Interactive Reply & Send Workflow

AI drafts are shown in an editable text area.

User can review and modify before sending directly from the app.

🚀 Live Demo & Testing Notes
This project uses sensitive Gmail scopes (read, send, modify). For a fully public production app, Google requires OAuth verification, which can take days or weeks.

For this technical assignment:

The OAuth consent screen is configured in testing mode.

A limited set of test user accounts are pre-authorized.

The app is fully functional for those test users, but may not work for arbitrary Google accounts without updating the test users list in the Google Cloud Console.

🛠️ Tech Stack & Architecture
Backend (Python, FastAPI)

Framework: FastAPI for high performance, async support, and automatic interactive docs.

Authentication: google-auth-oauthlib for server-side OAuth 2.0 token exchange and refresh.

Google API Integration: google-api-python-client for all Gmail API operations (read, modify, send, delete).

AI Integration: Modular client around the Mistral AI REST API (or pluggable LLM provider) for text generation and email replies.

State Management: In-memory dictionary for user sessions and conversation history for this assignment.

Frontend (React + Vite)

Framework: React with Vite for a fast, modern dev experience.

Authentication: @react-oauth/google for the client-side Google login flow.

API Communication: axios for HTTP requests to the FastAPI backend.

Styling: Clean, functional UI using standard CSS with a focus on readability and usability over heavy design.

⚙️ Setup and Local Installation
Prerequisites

Python 3.8+

Node.js v16+ and npm

Google Cloud Platform project with Gmail API enabled

OAuth 2.0 Client ID (Web application) from Google Cloud Console

API key from Mistral AI (or another LLM provider)

Clone the repository

bash
git clone <your-repo-link>
cd <your-repo-folder>
Backend setup

bash
cd backend

# Create your .env file with:
# GOOGLE_CLIENT_ID="your-google-client-id"
# GOOGLE_CLIENT_SECRET="your-google-client-secret"
# MISTRAL_API_KEY="your-mistral-api-key"

# Place your client_secret.json from Google Cloud Console in this directory.

# Install dependencies
pip install -r requirements.txt

# Run the backend server
uvicorn main:app --reload
Backend will be available at:

http://localhost:8000

Frontend setup

bash
# In a new terminal
cd frontend

# Create a .env file with:
# VITE_GOOGLE_CLIENT_ID="your-google-client-id"
# VITE_API_BASE_URL="http://localhost:8000"

# Install dependencies
npm install

# Run the frontend dev server
npm run dev
Frontend will be available at:

http://localhost:5173

Open the frontend URL, click “Sign in with Google”, and start interacting with the assistant.

📌 Assumptions & Limitations
In-Memory Storage

User sessions and conversation history are stored in memory only.

In production, this would be replaced by a persistent store (e.g., PostgreSQL, Redis) plus a secure session model (JWT or similar).

Single User Session

Current implementation is built around a single logical user (e.g., user_123) for simplicity.

A production-ready version would support multiple users with isolated data, proper auth, and multi-account management.

Simple Intent Recognition

Intent detection uses keyword and regex-based rules tailored to the assignment’s commands.

A large-scale system could integrate a dedicated NLU engine (Rasa, Dialogflow) or a fine-tuned LLM for more robust intent and entity extraction.

🧭 Possible Next Steps
Add persistent storage for sessions, email metadata, and conversation logs.

Extend to true multi-user, multi-account support.

Improve intent recognition using an NLU service or custom model.

Add richer categorization (spam, business, personal) and automation rules.
