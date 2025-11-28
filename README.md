AI-Powered Email Assistant

The AI-Powered Email Assistant is a mini platform built for the Constructure AI Applicant Challenge.
It showcases a production-grade workflow that blends:

Secure Google OAuth 2.0 authentication

A conversational AI chatbot interface

Intelligent email automation powered by NLP

Through natural language commands, users can read, summarize, reply to, and delete emails without manually navigating Gmail.

✨ Core Features
🔐 Secure Google OAuth 2.0 Authentication

Sign in with your Google account using industry-standard OAuth.

Requests Gmail permissions to read, modify, and send emails on the user’s behalf.

💬 Conversational AI Chatbot

Intuitive chat interface for issuing commands like:

“Show my latest emails”

“Summarize the third one”

“Draft a reply”

🧠 Advanced Intent Recognition

Automatically detects user intents:

fetch_emails

generate_reply

delete_email

Extracts context such as sender names, subject keywords, and positions like “first”, “second”, “last”.

🧵 Conversation Memory & Context Awareness

The assistant remembers the conversation flow.
After fetching emails, users can say:

“Delete the second one”

“Reply to the latest email”

…and the system correctly resolves them.

📧 Intelligent Email Automation

Read & Summarize recent emails or filtered by sender.

AI-Powered Replies with professional tone and contextual awareness.

Delete emails naturally, e.g., “delete the email from Amazon”.

✍️ Interactive Drafting Workflow

AI-generated drafts appear in an editable text area.

Users can refine and send emails directly from the app.

🚀 Live Demo & Testing Notes

This project uses sensitive Gmail scopes (read, send, modify).
Google requires OAuth verification for public apps — a long process.

For this assignment:

OAuth consent screen is in testing mode.

A predefined list of test users can access the app.

Non-listed accounts won’t be able to authenticate unless added in your Google Cloud Console.

🛠️ Tech Stack & Architecture
Backend — FastAPI (Python)

Framework: FastAPI (async, fast, auto-generated docs)

Auth: google-auth-oauthlib for secure OAuth 2.0 handling

Gmail API: google-api-python-client

AI Integration: Modular wrapper around Mistral AI API

State: In-memory session + conversation memory

Frontend — React + Vite

Framework: React with Vite

Auth: @react-oauth/google

API calls: axios

Focused UI built with clean, minimal CSS

⚙️ Installation & Setup
Prerequisites

Python 3.8+

Node.js 16+

Google Cloud project with Gmail API enabled

OAuth 2.0 Web Client ID & Secret

Mistral AI API key (or other LLM provider)

Clone the Repository
git clone <your-repo-link>
cd <your-repo-folder>

Backend Setup
cd backend

Create your .env file:
GOOGLE_CLIENT_ID="your-google-client-id"
GOOGLE_CLIENT_SECRET="your-google-client-secret"
MISTRAL_API_KEY="your-mistral-api-key"


Place your client_secret.json from Google Cloud inside /backend.

Install deps:
pip install -r requirements.txt

Start backend:
uvicorn main:app --reload


Backend runs at:
http://localhost:8000

Frontend Setup
cd frontend

Create a .env:
VITE_GOOGLE_CLIENT_ID="your-google-client-id"
VITE_API_BASE_URL="http://localhost:8000"

Install deps:
npm install

Start dev server:
npm run dev


Frontend runs at:
http://localhost:5173

📌 Assumptions & Limitations
🗃️ In-Memory Storage

Sessions & chat history stored only in memory.
A production version should use Redis/PostgreSQL + secure sessions.

👤 Single User Mode

The system currently uses one logical user (e.g., user_123).
Future versions should support multiple authenticated users with isolated data.

🔎 Simple Intent Recognition

Keyword + regex–based intent detection.
A scalable system would integrate LLM-based NLU (e.g., Rasa, Dialogflow).

🧭 Future Improvements

🔹 Add persistent storage (Redis/PostgreSQL)
🔹 Multi-user + multi-account support
🔹 Better NLU with fine-tuned models
🔹 Categorization (spam, business, personal)
🔹 Rules & automation engine
