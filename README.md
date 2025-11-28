# Gmail AI Assistant

A full-stack application that uses FastAPI backend and React frontend to manage Gmail emails with AI-powered reply generation.

## Project Structure

```
Final/
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   ├── .env
│   └── client_secret.json
└── frontend/
    ├── src/
    │   ├── components/
    │   │   ├── Login.jsx
    │   │   └── Dashboard.jsx
    │   ├── App.jsx
    │   ├── App.css
    │   └── main.jsx
    ├── index.html
    ├── vite.config.js
    └── package.json
```

## Setup Instructions

### Prerequisites

- Python 3.8+
- Node.js 16+
- Google Cloud OAuth credentials (Client ID & Secret)
- OpenAI API Key

### Backend Setup

1. Navigate to the backend directory:
   ```powershell
   cd backend
   ```

2. Create a virtual environment (optional but recommended):
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

3. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```

4. The `.env` and `client_secret.json` files are already configured with your API keys.

5. Start the backend server:
   ```powershell
   uvicorn main:app --reload
   ```

   The backend will run at `http://localhost:8000`

### Frontend Setup

1. In a new terminal, navigate to the frontend directory:
   ```powershell
   cd frontend
   ```

2. Install dependencies:
   ```powershell
   npm install
   ```

3. Start the development server:
   ```powershell
   npm run dev
   ```

   The frontend will run at `http://localhost:5173`

## Usage

1. Open `http://localhost:5173` in your browser
2. Click "Sign in with Google" to authenticate with your Google account
3. Grant the necessary permissions for Gmail access
4. View your 5 most recent emails
5. Generate AI-powered replies or delete emails as needed

## Features

- **Google OAuth Authentication**: Secure login with Google accounts
- **Email Fetching**: Display the 5 most recent emails from your inbox
- **AI Reply Generation**: Uses OpenAI to generate professional email replies
- **Email Management**: Delete emails directly from the dashboard
- **Chat Interface**: Real-time conversation log with system messages

## API Endpoints

- `POST /auth/google` - Exchange authorization code for access tokens
- `GET /emails/recent` - Fetch 5 most recent emails
- `POST /emails/generate-reply` - Generate AI reply for email content
- `POST /emails/delete` - Delete an email by message ID

## Important Notes

- Credentials are stored in-memory for this demo (use a database in production)
- Keep your API keys secure - never commit `.env` or `client_secret.json` to version control
- The app uses OAuth2 flow for secure Google authentication
- All sensitive API calls are handled by the backend to protect credentials

## Troubleshooting

- **"Invalid credentials"**: Ensure `client_secret.json` is in the backend directory
- **CORS errors**: Make sure both frontend and backend are running with correct origins
- **Authentication fails**: Verify your Google OAuth credentials are correct in `.env`
- **API errors**: Check that OpenAI API key is valid and has remaining credits
