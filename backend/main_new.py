import os
import json
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests

# Google API Imports
import google.oauth2.credentials
import google_auth_oauthlib.flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import parseaddr

# Mistral AI Import
try:
    from mistralai.client import MistralClient
    from mistralai.models.chat_message import ChatMessage
except ImportError:
    print("[WARNING] Mistral AI package not found. Install with: pip install mistralai")
    MistralClient = None
    ChatMessage = None

# --- CONFIGURATION ---
load_dotenv()

# --- FASTAPI APP INITIALIZATION ---
app = FastAPI()

origins = [
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- DEBUG ENDPOINT ---
@app.get("/debug/config")
def debug_config():
    """Check your OAuth configuration"""
    try:
        with open('client_secret.json', 'r') as f:
            config = json.load(f)
        web_config = config.get('web', config.get('installed'))
        return {
            "client_id": web_config.get('client_id'),
            "redirect_uris": web_config.get('redirect_uris'),
            "token_uri": web_config.get('token_uri'),
            "has_client_secret": bool(web_config.get('client_secret')),
            "config_type": "web" if "web" in config else "installed"
        }
    except Exception as e:
        return {"error": str(e)}

# --- IN-MEMORY STORAGE (FOR SIMPLICITY) ---
# In a real app, this would be a secure database.
user_credentials = {}

# --- DATA MODELS (PYDANTIC) ---
class AuthCode(BaseModel):
    code: str = None
    access_token: str = None
    token_type: str = None
    expires_in: int = None

class EmailContent(BaseModel):
    content: str
    
class MessageId(BaseModel):
    message_id: str


class SendRequest(BaseModel):
    message_id: str
    reply_text: str
    send_now: bool = True

# --- AUTHENTICATION FLOW ---
@app.post("/auth/google")
def auth_google(auth_data: AuthCode):
    """
    Handles Google authentication.
    Can accept either:
    1. Authorization code (code exchange flow)
    2. Direct access token (implicit flow)
    """
    try:
        print("\n========== STARTING OAUTH AUTHENTICATION ==========")
        
        # Load client secrets
        with open('client_secret.json', 'r') as f:
            client_config = json.load(f)
        
        web_config = client_config.get('web', client_config.get('installed'))
        client_id = web_config['client_id']
        token_uri = web_config['token_uri']
        
        print(f"[DEBUG] Client ID: {client_id}")
        
        # Check if we received an access token directly (implicit flow)
        if auth_data.access_token:
            print(f"[INFO] Received direct access token (implicit flow)")
            print(f"[DEBUG] Access token (first 20 chars): {auth_data.access_token[:20]}...")
            
            # Verify the token is valid by making a test call to Gmail API
            try:
                verify_response = requests.get(
                    'https://www.googleapis.com/gmail/v1/users/me/profile',
                    headers={'Authorization': f'Bearer {auth_data.access_token}'}
                )
                
                if verify_response.status_code == 200:
                    print(f"[SUCCESS] Access token verified with Gmail API!")
                    
                    user_id = "user_123"
                    user_credentials[user_id] = {
                        'token': auth_data.access_token,
                        'refresh_token': None,
                        'token_uri': token_uri,
                        'client_id': client_id,
                        'client_secret': web_config['client_secret'],
                        'scopes': ['https://www.googleapis.com/auth/gmail.readonly',
                                  'https://www.googleapis.com/auth/gmail.send',
                                  'https://www.googleapis.com/auth/gmail.modify']
                    }
                    print(f"[DEBUG] User credentials stored for user_id: {user_id}")
                    print(f"========== OAUTH AUTHENTICATION COMPLETE ==========\n")
                    return {"status": "success", "user_id": user_id}
                else:
                    print(f"[ERROR] Token verification failed: {verify_response.status_code}")
                    raise Exception(f"Token verification failed: {verify_response.text}")
                    
            except Exception as e:
                print(f"[ERROR] Token verification error: {str(e)}")
                raise Exception(f"Token verification failed: {str(e)}")
        
        # Otherwise, handle authorization code flow
        elif auth_data.code:
            print(f"[INFO] Received authorization code (code flow)")
            print(f"[DEBUG] Authorization Code (first 20 chars): {auth_data.code[:20]}...")
            
            # Try with multiple redirect URIs
            redirect_uris_to_try = ['http://localhost:5173/', 'http://localhost:5173/api/oauth2/callback', 'postMessage']
            
            for redirect_uri in redirect_uris_to_try:
                print(f"\n[DEBUG] Trying with redirect_uri: {redirect_uri}")
                
                payload = {
                    'code': auth_data.code,
                    'client_id': client_id,
                    'client_secret': web_config['client_secret'],
                    'redirect_uri': redirect_uri,
                    'grant_type': 'authorization_code'
                }
                
                token_response = requests.post(token_uri, data=payload)
                
                if token_response.status_code == 200:
                    token_data = token_response.json()
                    print(f"\n[SUCCESS] Successfully obtained tokens with redirect_uri: {redirect_uri}!")
                    
                    user_id = "user_123"
                    user_credentials[user_id] = {
                        'token': token_data.get('access_token'),
                        'refresh_token': token_data.get('refresh_token'),
                        'token_uri': token_uri,
                        'client_id': client_id,
                        'client_secret': web_config['client_secret'],
                        'scopes': token_data.get('scope', '').split()
                    }
                    print(f"[DEBUG] User credentials stored for user_id: {user_id}")
                    print(f"========== OAUTH AUTHENTICATION COMPLETE ==========\n")
                    return {"status": "success", "user_id": user_id}
            
            raise Exception("Token exchange failed with all attempted redirect URIs")
        
        else:
            raise Exception("No access token or authorization code provided")
        
    except Exception as e:
        print(f"\n[CRITICAL ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
        print(f"========== OAUTH AUTHENTICATION FAILED ==========\n")
        raise HTTPException(status_code=400, detail=f"Error fetching token: {str(e)}")


# --- GMAIL API FUNCTIONS ---
def get_gmail_service(user_id: str):
    """Creates a Gmail service object from stored credentials."""
    creds_dict = user_credentials.get(user_id)
    if not creds_dict:
        raise HTTPException(status_code=401, detail="User not authenticated")
    
    credentials = google.oauth2.credentials.Credentials(**creds_dict)
    if not credentials or not credentials.valid:
        raise HTTPException(status_code=401, detail="Invalid or expired credentials")

    try:
        service = build('gmail', 'v1', credentials=credentials)
        return service
    except HttpError as error:
        raise HTTPException(status_code=500, detail=f"Failed to create Gmail service: {error}")


@app.get("/emails/recent")
def read_recent_emails(user_id: str = "user_123"):
    """Fetches the 5 most recent emails and returns a summary."""
    service = get_gmail_service(user_id)
    try:
        # Get the list of message IDs
        results = service.users().messages().list(userId='me', labelIds=['INBOX'], maxResults=5).execute()
        messages = results.get('messages', [])
        
        email_summaries = []
        if not messages:
            return []

        for message in messages:
            msg = service.users().messages().get(userId='me', id=message['id']).execute()
            payload = msg.get('payload', {})
            headers = payload.get('headers', [])
            
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
            sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown Sender')
            snippet = msg.get('snippet', 'No content available.')

            email_summaries.append({
                "id": msg['id'],
                "sender": sender,
                "subject": subject,
                "snippet": snippet
            })
            
        return email_summaries
    except HttpError as error:
        raise HTTPException(status_code=500, detail=f"An error occurred with the Gmail API: {error}")


# --- AI AND EMAIL ACTIONS ---
@app.post("/emails/generate-reply")
def generate_ai_response(email_data: EmailContent):
    """Generates an AI reply based on email content using Mistral AI."""
    try:
        print("\n========== GENERATING AI REPLY ==========")
        print(f"[DEBUG] Email content length: {len(email_data.content)}")

        # Prefer REST call to Mistral API to avoid depending on the installed SDK
        api_key = os.getenv("MISTRAL_API_KEY")
        model = os.getenv("MISTRAL_MODEL", "mistral-small")
        if not api_key:
            print("[ERROR] MISTRAL_API_KEY not set in environment")
            raise Exception("MISTRAL_API_KEY not set in environment")

        print(f"[DEBUG] Mistral API Key found (length: {len(api_key)})")
        endpoint = os.getenv("MISTRAL_API_URL", "https://api.mistral.ai/v1/chat/completions")

        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": "You are a professional and helpful email assistant. Write clear, concise, and context-aware replies that are ready to be sent."},
                {"role": "user", "content": f"Based on this email content, write a professional reply:\n\n{email_data.content}"}
            ],
            "temperature": 0.7,
            "max_tokens": 150
        }

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        print(f"[INFO] Calling Mistral REST API at {endpoint} with model {model}...")

        resp = requests.post(endpoint, headers=headers, json=payload, timeout=30)
        try:
            data = resp.json()
        except Exception:
            data = None

        if resp.status_code != 200:
            print(f"[ERROR] Mistral REST API returned status {resp.status_code}: {resp.text}")
            # Fallback reply to avoid 500s for the frontend
            fallback = (
                "[AI Unavailable] The AI service returned an error. "
                "Please try again later or edit this suggested reply:\n\n"
                "Thanks for the update. I will review and follow up with next steps shortly.\n\n"
                "Best regards,\n[Your Name]"
            )
            return {"reply": fallback}

        # Robustly extract reply text from common response shapes
        reply_text = None
        try:
            # Typical chat-style response: choices[0].message.content
            if isinstance(data, dict):
                choices = data.get("choices")
                if choices and isinstance(choices, list):
                    first = choices[0]
                    # nested message object
                    if isinstance(first, dict):
                        msg = first.get("message") or first.get("delta")
                        if isinstance(msg, dict):
                            reply_text = msg.get("content") or msg.get("text")
                        else:
                            # sometimes 'text' or string
                            reply_text = first.get("text") or first.get("content")

                # other possible top-level formats
                if not reply_text:
                    # try `output` or `outputs`
                    if "output" in data and isinstance(data["output"], str):
                        reply_text = data["output"]
                    elif "outputs" in data and isinstance(data["outputs"], list) and data["outputs"]:
                        # sometimes outputs is a list of dicts
                        o = data["outputs"][0]
                        if isinstance(o, dict):
                            reply_text = o.get("text") or o.get("content") or str(o)
                        else:
                            reply_text = str(o)

            if not reply_text:
                # As a last resort, string-ify the JSON
                reply_text = json.dumps(data)
        except Exception as ex:
            print(f"[WARN] Failed to parse Mistral response: {ex}")
            reply_text = resp.text or ""

        reply_text = (reply_text or "").strip()

        print(f"[SUCCESS] Generated reply (length: {len(reply_text)} chars)")
        print(f"[DEBUG] Reply preview: {reply_text[:100]}...")
        print(f"========== AI REPLY GENERATION COMPLETE ==========")

        return {"reply": reply_text}
    except Exception as e:
        print(f"\n[ERROR] Mistral AI error: {str(e)}")
        print(f"[DEBUG] Exception type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        print(f"========== AI REPLY GENERATION FAILED ==========\n")
        raise HTTPException(status_code=500, detail=f"Error with Mistral AI: {str(e)}")

@app.post("/emails/delete")
def delete_email(message: MessageId, user_id: str = "user_123"):
    """Deletes a specific email by its message ID."""
    service = get_gmail_service(user_id)
    try:
        # Using trash is safer than permanent delete
        service.users().messages().trash(userId='me', id=message.message_id).execute()
        return {"status": "success", "message": f"Email with ID {message.message_id} moved to trash."}
    except HttpError as error:
        raise HTTPException(status_code=500, detail=f"Failed to delete email: {error}")


@app.post("/emails/send")
def send_email_reply(payload: SendRequest, user_id: str = "user_123"):
    """Sends a reply to the original email using the Gmail API."""
    service = get_gmail_service(user_id)
    try:
        # Fetch original message to extract headers
        original = service.users().messages().get(userId='me', id=payload.message_id, format='full').execute()
        headers = {h['name']: h['value'] for h in original.get('payload', {}).get('headers', [])}

        orig_from = headers.get('From', '')
        orig_subject = headers.get('Subject', '')
        orig_message_id = headers.get('Message-ID') or headers.get('Message-Id')

        # Extract email address from From header
        _, from_email = parseaddr(orig_from)
        if not from_email:
            raise HTTPException(status_code=400, detail="Unable to determine recipient email from original message")

        # Build reply subject
        reply_subject = orig_subject if orig_subject.lower().startswith('re:') else f"Re: {orig_subject}"

        # Create MIME message
        msg = MIMEMultipart()
        msg['To'] = from_email
        msg['Subject'] = reply_subject
        if orig_message_id:
            msg['In-Reply-To'] = orig_message_id
            msg['References'] = orig_message_id

        # Set body
        body = MIMEText(payload.reply_text, 'plain')
        msg.attach(body)

        raw_bytes = base64.urlsafe_b64encode(msg.as_bytes())
        raw_str = raw_bytes.decode('utf-8')

        send_response = service.users().messages().send(userId='me', body={'raw': raw_str}).execute()

        return {"status": "sent", "gmail_message_id": send_response.get('id')}

    except HttpError as error:
        raise HTTPException(status_code=500, detail=f"Failed to send reply: {error}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
