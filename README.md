AI-Powered Email Assistant
Welcome to the AI-Powered Email Assistant, a technical assignment built for the Constructure AI Applicant Challenge. This project is a mini-platform designed to demonstrate a production-grade workflow, integrating secure authentication, a conversational AI interface, and intelligent email automation.
The application allows users to securely log in with their Google account, view recent emails, and leverage a sophisticated AI chatbot to read, summarize, reply to, and delete emails using natural language commands.
✨ Core Features
This project was built to be more than just a simple dashboard; it's a demonstration of a stateful, context-aware AI assistant.
Secure Google OAuth 2.0 Authentication: Users sign in securely using their Google account. The application requests the necessary permissions to read, modify, and send emails on the user's behalf.
Conversational AI Chatbot: The central feature is a true chatbot interface that understands natural language commands. It goes beyond simple if/else logic to provide a more intuitive user experience.
Advanced Intent Recognition: The chatbot's backend can parse user commands to detect their intent (e.g., fetch_emails, delete_email, generate_reply) and extract key entities (e.g., senders, subject keywords, and email positions like "first" or "last").
Conversation Memory & Context Awareness: The assistant remembers the context of the conversation. After fetching a list of emails, a user can give follow-up commands like "delete the second one" or "draft a reply to the latest email," and the assistant will understand the reference.
Intelligent Email Automation:
Read & Summarize: Fetch recent emails from the inbox or search for emails from specific senders.
AI-Powered Replies: Generate context-aware, professional replies to any email with a single command.
Natural Language Deletion: Delete emails by referencing the sender or their position in the conversation history (e.g., "delete the email from Amazon").
Interactive Reply & Send Workflow: AI-generated replies are presented in an editable text area, giving the user full control to review and modify the content before sending it directly from the application.
🚀 Live Demo & Status
Important Note on Deployment & Testing:
This application is currently in a testing phase. To enable the sensitive scopes required by the Gmail API (read, send, modify), a production application must undergo a formal verification process by Google, which can take several days or weeks.
To facilitate this technical assignment, the OAuth consent screen has been configured with a limited set of personal test user accounts. Therefore, the live deployment may not be publicly accessible for all Google accounts. The project has been thoroughly tested and is fully functional with these pre-authorized test users.
🛠️ Tech Stack & Architecture
This project is a modern full-stack application with a clear separation between the frontend and the backend.
Backend (Python, FastAPI)
Framework: FastAPI for its high performance, asynchronous capabilities, and automatic API documentation.
Authentication: google-auth-oauthlib to handle the complex server-side OAuth 2.0 token exchange flow.
Google API Integration: google-api-python-client for all interactions with the Gmail API.
AI Integration: A modular design that uses the official REST API for Mistral AI, providing robust and intelligent text generation.
State Management: An in-memory dictionary is used to manage user sessions and conversation history for this assignment.
Frontend (React)
Framework: React (with Vite) for a fast and modern development experience.
Authentication: @react-oauth/google to handle the client-side Google Login flow seamlessly.
API Communication: axios for all requests to the backend API.
Styling: Clean, functional UI with standard CSS to demonstrate a focus on usability over complex design.
⚙️ Setup and Local Installation
To run this project on your local machine, please follow these steps.
Prerequisites
Python 3.8+
Node.js v16+ and npm
A Google Cloud Platform project with the Gmail API enabled.
An OAuth 2.0 Client ID from the Google Cloud Console.
An API Key from Mistral AI (or another LLM provider).
1. Clone the Repository```bash
git clone [your-repo-link]
cd [your-repo-folder]
code
Code
#### 2. Backend Setup
```bash
cd backend

# Create and populate your .env file
# Create a file named .env and add your credentials:
# GOOGLE_CLIENT_ID="your-google-client-id"
# GOOGLE_CLIENT_SECRET="your-google-client-secret"
# MISTRAL_API_KEY="your-mistral-api-key"

# Download your client_secret.json from the Google Cloud Console
# and place it in this directory.

# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn main:app --reload
The backend will be running at http://localhost:8000.
3. Frontend Setup
code
Bash
# In a new terminal
cd frontend

# Create and populate your .env file
# Create a file named .env and add your Google Client ID:
# VITE_GOOGLE_CLIENT_ID="your-google-client-id"
# VITE_API_BASE_URL="http://localhost:8000"

# Install dependencies
npm install

# Run the development server
npm run dev
```The frontend will be running at `http://localhost:5173`.

##  assumptions & Limitations

*   **In-Memory Storage:** For this assignment, user sessions and conversation history are stored in memory. In a production environment, this would be replaced with a persistent database (like PostgreSQL or Redis) and a secure JWT-based session management system.
*   **Single User Session:** The current implementation is designed for a single user (`user_123`) for simplicity. A production system would have a robust multi-user authentication and data isolation architecture.
*   **Simple Intent Recognition:** The intent recognition uses a keyword and regex-based approach, which is effective for this assignment. A larger-scale system might leverage a dedicated NLU service like Rasa, Dialogflow, or a fine-tuned language model.