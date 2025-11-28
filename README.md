# AI-Powered Email Assistant

The **AI-Powered Email Assistant** is a mini platform built for the **Constructure AI Applicant Challenge**.  
It demonstrates a production-style workflow combining:

- Secure Google OAuth 2.0 authentication  
- A conversational AI chatbot  
- Intelligent email automation powered by NLP  

Users can naturally **read, summarize, reply to, and delete emails** using natural language.

---

## ✨ Core Features

### 🔐 Secure Google OAuth 2.0 Authentication
- Sign in using your Google account.
- Requests permissions to **read, send, and modify** emails.

### 💬 Conversational AI Chatbot
- Natural language interface for all email actions.
- Example commands:  
  - “Show my recent emails”  
  - “Summarize the second one”  
  - “Draft a reply”  
  - “Delete Amazon’s email”  

### 🧠 Advanced Intent Recognition
Automatically detects:
- `fetch_emails`
- `generate_reply`
- `delete_email`

Extracts useful entities:
- Sender names  
- Subject keywords  
- Positions like *first, second, last*

### 🧵 Conversation Memory & Context Awareness
Understands references based on previous actions:
- “Delete the second one”
- “Reply to the latest email”

### 📧 Intelligent Email Automation
- Fetches and summarizes recent emails.
- Drafts professional replies using AI.
- Deletes emails naturally using text commands.

### ✍️ Interactive Reply Workflow
- AI drafts appear in an editable text box.
- Users can refine and send emails instantly.

---

## 🚀 Demo & Testing Notes

Gmail uses sensitive scopes (`read`, `modify`, `send`).

- OAuth Consent Screen is in **testing mode**.
- Only **pre-approved test users** can access the app.
- Additional accounts must be added manually in Google Cloud Console.

---

## 🛠️ Tech Stack & Architecture

### Backend — FastAPI (Python)
- **FastAPI** for backend APIs
- **google-auth-oauthlib** for OAuth 2.0
- **google-api-python-client** for Gmail API operations
- **Mistral AI API** for LLM-based email replies
- In-memory storage for session & conversation history

### Frontend — React + Vite
- **React** with **Vite**
- **@react-oauth/google** for Google login
- **axios** for API requests
- Clean, minimal UI using CSS

---

## ⚙️ Installation & Setup

### Prerequisites
- Python **3.8+**
- Node.js **16+**
- Gmail API enabled in Google Cloud
- OAuth 2.0 **Client ID & Secret**
- **Mistral AI API key**

---

📌 Assumptions & Limitations

🗂️ In-Memory Storage
Sessions and conversation history are stored in RAM only.
Production apps should use Redis/PostgreSQL and JWT-based sessions.

👤 Single User Mode
Currently supports one logical user (user_123).
Should be extended to real multi-user support.

🔎 Simple Intent Recognition
Uses keyword + regex-based rules.
Production-ready version should integrate a real NLU engine or a fine-tuned model.

🧭 Future Improvements
Add persistent storage (Redis/PostgreSQL)
Multi-user & multi-account support
Better NLU using LLM-based classifiers
Email categorization (spam, business, personal)
Automation rules engine

## 📦 Clone the Repository

```bash
git clone <your-repo-link>
cd <your-repo-folder>
🖥️ Backend Setup
cd backend

Create .env file:
GOOGLE_CLIENT_ID="your-google-client-id"
GOOGLE_CLIENT_SECRET="your-google-client-secret"
MISTRAL_API_KEY="your-mistral-api-key"


Place your client_secret.json (downloaded from Google Cloud Console) into the /backend directory.

Install dependencies:
pip install -r requirements.txt

Run backend:
uvicorn main:app --reload


Backend runs at ⇢ http://localhost:8000

🌐 Frontend Setup
cd frontend

Create .env file:
VITE_GOOGLE_CLIENT_ID="your-google-client-id"
VITE_API_BASE_URL="http://localhost:8000"

Install dependencies:
npm install

Start dev server:
npm run dev


Frontend runs at ⇢ http://localhost:5173
