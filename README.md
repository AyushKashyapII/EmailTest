# AI-Powered Email Assistant

The **AI-Powered Email Assistant** is a mini platform built for the **Constructure AI Applicant Challenge**.  
It showcases a production-style workflow combining:

- Secure Google OAuth 2.0 authentication  
- A conversational AI chatbot  
- Intelligent email automation powered by NLP  

Users can naturally **read, summarize, reply to, and delete emails** without manually navigating Gmail.

---

## ✨ Core Features

### 🔐 Secure Google OAuth 2.0 Authentication
- Sign in securely with your Google account.
- Requests permissions to **read, modify, and send** emails.

### 💬 Conversational AI Chatbot
- Central chat interface that understands natural language.
- Users can say: *“show my emails”, “summarize the first one”, “draft a reply”, “delete Amazon’s email”*, etc.

### 🧠 Advanced Intent Recognition
Detects intents like:
- `fetch_emails`
- `generate_reply`
- `delete_email`

Extracts entities such as sender names, subject keywords, or positions like *first, second, last*.

### 🧵 Conversation Memory
Understands context across turns:

- “Delete the second one”  
- “Draft a reply to the latest email”

…and resolves references accurately based on previous actions.

### 📧 Intelligent Email Automation
- **Read & summarize** your recent inbox emails.
- **Reply** with AI-generated, professional responses.
- **Delete** emails naturally with commands like “delete the email from Amazon”.

### ✍️ Interactive Reply Workflow
- AI drafts appear in an editable text area.
- User can refine and send emails directly.

---

## 🚀 Live Demo & Testing Notes

This project uses sensitive Gmail scopes.  
Google requires full OAuth verification for public use (takes days/weeks).

For this assignment:

- OAuth is in **testing mode**  
- Only pre-approved **test users** can log in  
- Other users must be added manually in the Google Cloud Console  

---

## 🛠️ Tech Stack & Architecture

### **Backend (FastAPI + Python)**
- **FastAPI** for async, high-performance backend
- **google-auth-oauthlib** for OAuth 2.0
- **google-api-python-client** for Gmail API operations (read, send, delete)
- **Mistral AI API** for LLM-based email replies
- In-memory session + conversation history

### **Frontend (React + Vite)**
- **React + Vite** for fast frontend dev
- **@react-oauth/google** for Google login
- **axios** for API calls
- Clean, minimal UI using CSS

---

## ⚙️ Installation & Setup

### Prerequisites
- Python **3.8+**
- Node.js **16+**
- Google Cloud project with Gmail API enabled
- OAuth 2.0 Client ID & Secret
- Mistral AI API key

---

## 📦 Clone the Repository

```bash
git clone <your-repo-link>
cd <your-repo-folder>
🖥️ Backend Setup
cd backend

Create your .env file:
GOOGLE_CLIENT_ID="your-google-client-id"
GOOGLE_CLIENT_SECRET="your-google-client-secret"
MISTRAL_API_KEY="your-mistral-api-key"


Place your client_secret.json from Google Cloud Console inside /backend.

Install dependencies
pip install -r requirements.txt

Run backend
uvicorn main:app --reload


Backend server runs at:

http://localhost:8000

🌐 Frontend Setup
cd frontend

Create .env file:
VITE_GOOGLE_CLIENT_ID="your-google-client-id"
VITE_API_BASE_URL="http://localhost:8000"

Install dependencies
npm install

Run frontend
npm run dev


Frontend is available at:

http://localhost:5173

📌 Assumptions & Limitations
🗂️ In-Memory Storage

User sessions & conversation history stored only in RAM.

Production-ready app should use Redis/PostgreSQL + secure session tokens.

👤 Single User Session

Current build uses a single logical user (user_123).

Multi-user support requires proper DB & auth.

🔎 Simple Intent Recognition

Rule-based + regex.

Real systems should use LLM-based NLU (Rasa, Dialogflow, fine-tuned models).

🧭 Future Improvements

Persistent database storage

Multi-user & multi-account support

Advanced NLU models

Email categorization (spam, business, personal)

Automated rules engine
