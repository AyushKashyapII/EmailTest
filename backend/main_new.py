import os
import json
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import re
from typing import List, Dict, Optional
from datetime import datetime

# Google API Imports
import google.oauth2.credentials
import google_auth_oauthlib.flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import parseaddr

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

# --- IN-MEMORY STORAGE ---
user_credentials = {}
# Conversation memory storage per user
conversation_memory = {}
# Email cache for context
email_cache = {}

# --- DATA MODELS ---
class AuthCode(BaseModel):
    code: str = None
    access_token: str = None
    token_type: str = None
    expires_in: int = None

class EmailContent(BaseModel):
    content: str
    
class MessageId(BaseModel):
    message_id: str

class ChatCommand(BaseModel):
    command: str
    context: Optional[Dict] = None  # Allow frontend to send additional context

class SendRequest(BaseModel):
    message_id: str
    reply_text: str
    send_now: bool = True

class ConversationMessage(BaseModel):
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: str
    action_taken: Optional[str] = None

# --- CONVERSATION MEMORY MANAGEMENT ---
def add_to_conversation(user_id: str, role: str, content: str, action_taken: Optional[str] = None):
    """Add a message to the conversation history."""
    if user_id not in conversation_memory:
        conversation_memory[user_id] = []
    
    conversation_memory[user_id].append({
        "role": role,
        "content": content,
        "timestamp": datetime.now().isoformat(),
        "action_taken": action_taken
    })
    
    # Keep only last 20 messages to avoid memory issues
    if len(conversation_memory[user_id]) > 20:
        conversation_memory[user_id] = conversation_memory[user_id][-20:]

def get_conversation_context(user_id: str, last_n: int = 5) -> str:
    """Get recent conversation context for AI understanding."""
    if user_id not in conversation_memory:
        return ""
    
    recent = conversation_memory[user_id][-last_n:]
    context_str = "Recent conversation:\n"
    for msg in recent:
        context_str += f"{msg['role']}: {msg['content']}\n"
    return context_str

def get_last_action(user_id: str) -> Optional[str]:
    """Get the last action taken by the assistant."""
    if user_id not in conversation_memory:
        return None
    
    for msg in reversed(conversation_memory[user_id]):
        if msg.get('action_taken'):
            return msg['action_taken']
    return None

# --- EMAIL CACHE MANAGEMENT ---
def cache_emails(user_id: str, emails: List[Dict]):
    """Cache fetched emails for context reference."""
    email_cache[user_id] = {
        "emails": emails,
        "timestamp": datetime.now().isoformat()
    }

def get_cached_emails(user_id: str) -> List[Dict]:
    """Get cached emails if available."""
    if user_id in email_cache:
        return email_cache[user_id].get("emails", [])
    return []

def find_email_by_reference(user_id: str, reference: str) -> Optional[Dict]:
    """Find an email by various references (sender, subject keywords, position)."""
    cached = get_cached_emails(user_id)
    if not cached:
        return None
    
    reference_lower = reference.lower()
    
    # Check if reference is a position (first, last, latest, etc.)
    if any(word in reference_lower for word in ['first', 'latest', 'recent', 'newest']):
        return cached[0] if cached else None
    if 'last' in reference_lower or 'oldest' in reference_lower:
        return cached[-1] if cached else None
    
    # Check for number reference (e.g., "second email", "3rd email")
    number_match = re.search(r'(\d+)(st|nd|rd|th)?', reference_lower)
    if number_match:
        idx = int(number_match.group(1)) - 1
        if 0 <= idx < len(cached):
            return cached[idx]
    
    # Search by sender or subject
    for email in cached:
        sender = email.get('sender', '').lower()
        subject = email.get('subject', '').lower()
        if reference_lower in sender or reference_lower in subject:
            return email
    
    return None

# --- ENHANCED INTENT RECOGNITION ---
def detect_intent_and_entities(command: str, user_id: str) -> Dict:
    """
    Enhanced intent detection with entity extraction.
    Returns a dictionary with intent, entities, and confidence.
    """
    command_lower = command.lower().strip()
    
    # Define intents with multiple trigger patterns
    intents = {
        "greet": ["hello", "hi", "hey", "greetings", "good morning", "good afternoon"],
        "help": ["help", "what can you do", "commands", "how to", "guide", "explain"],
        "fetch_emails": ["fetch", "read", "get", "show", "display", "list", "check", "see"],
        "delete_email": ["delete", "remove", "trash", "get rid of"],
        "generate_reply": ["reply", "respond", "answer", "draft", "compose"],
        "send_email": ["send", "deliver", "dispatch"],
        "search_email": ["search", "find", "look for", "locate"],
        "status": ["status", "what did you do", "last action", "what happened"],
    }
    
    detected_intent = "unknown"
    confidence = 0.0
    
    # Intent detection
    for intent, keywords in intents.items():
        matches = sum(1 for keyword in keywords if keyword in command_lower)
        if matches > 0:
            current_confidence = matches / len(keywords)
            if current_confidence > confidence:
                confidence = current_confidence
                detected_intent = intent
    
    # Entity extraction
    entities = {
        "sender": None,
        "subject": None,
        "count": 5,  # default
        "email_reference": None,
        "time_reference": None
    }
    
    # Extract sender (from X)
    sender_match = re.search(r'from\s+([\w.@\s-]+)', command_lower)
    if sender_match:
        entities["sender"] = sender_match.group(1).strip()
    
    # Extract subject keywords
    subject_match = re.search(r'(about|subject|regarding)\s+["\']?([^"\']+)["\']?', command_lower)
    if subject_match:
        entities["subject"] = subject_match.group(2).strip()
    
    # Extract count
    count_match = re.search(r'(\d+|last|latest|recent)', command_lower)
    if count_match:
        count_str = count_match.group(1)
        if count_str.isdigit():
            entities["count"] = int(count_str)
    
    # Extract email references (this, that, it, the email, etc.)
    if any(word in command_lower for word in ['this', 'that', 'it', 'the email', 'that email']):
        entities["email_reference"] = "contextual"
    elif any(word in command_lower for word in ['first', 'second', 'third', 'last', 'latest']):
        entities["email_reference"] = command_lower
    
    return {
        "intent": detected_intent,
        "confidence": confidence,
        "entities": entities,
        "original_command": command
    }

# --- GREETING AND HELP ---
def generate_greeting(user_id: str) -> str:
    """Generate a personalized greeting."""
    return """Hello! 👋 I'm your AI Email Assistant. I can help you manage your emails efficiently.

Here's what I can do for you:
• **Read emails** - "Show me my latest 5 emails" or "Fetch emails from John"
• **Generate replies** - "Draft a reply to the first email" or "Help me respond to Sarah's email"
• **Delete emails** - "Delete the email from newsletter@company.com"
• **Search emails** - "Find emails about project updates"

Just tell me what you need, and I'll take care of it! What would you like to do?"""

def generate_help_message() -> str:
    """Generate help message with examples."""
    return """I can assist you with the following email tasks:

📧 **Reading Emails:**
- "Show me my latest emails"
- "Read the last 10 emails"
- "Get emails from john@example.com"

✍️ **Generating Replies:**
- "Draft a reply to the first email"
- "Help me respond to Sarah's message"

🗑️ **Deleting Emails:**
- "Delete the email from Amazon"
- "Remove the first email"

🔍 **Searching:**
- "Find emails about invoices"
- "Search for emails from my boss"

📊 **Status:**
- "What did you do last?"
- "Show me the status"

Just ask naturally, and I'll understand what you need!"""

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

# --- AUTHENTICATION FLOW ---
@app.post("/auth/google")
def auth_google(auth_data: AuthCode):
    """Handles Google authentication with both code and token flows."""
    try:
        print("\n========== STARTING OAUTH AUTHENTICATION ==========")
        
        with open('client_secret.json', 'r') as f:
            client_config = json.load(f)
        
        web_config = client_config.get('web', client_config.get('installed'))
        client_id = web_config['client_id']
        token_uri = web_config['token_uri']
        
        print(f"[DEBUG] Client ID: {client_id}")
        
        if auth_data.access_token:
            print(f"[INFO] Received direct access token (implicit flow)")
            
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
                
                # Initialize conversation with greeting
                add_to_conversation(user_id, "assistant", generate_greeting(user_id))
                
                print(f"========== OAUTH AUTHENTICATION COMPLETE ==========\n")
                return {"status": "success", "user_id": user_id}
            else:
                raise Exception(f"Token verification failed: {verify_response.text}")
        
        elif auth_data.code:
            print(f"[INFO] Received authorization code (code flow)")
            
            redirect_uris_to_try = ['http://localhost:5173/', 'http://localhost:5173/api/oauth2/callback', 'postMessage']
            
            for redirect_uri in redirect_uris_to_try:
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
                    
                    user_id = "user_123"
                    user_credentials[user_id] = {
                        'token': token_data.get('access_token'),
                        'refresh_token': token_data.get('refresh_token'),
                        'token_uri': token_uri,
                        'client_id': client_id,
                        'client_secret': web_config['client_secret'],
                        'scopes': token_data.get('scope', '').split()
                    }
                    
                    # Initialize conversation with greeting
                    add_to_conversation(user_id, "assistant", generate_greeting(user_id))
                    
                    print(f"========== OAUTH AUTHENTICATION COMPLETE ==========\n")
                    return {"status": "success", "user_id": user_id}
            
            raise Exception("Token exchange failed with all attempted redirect URIs")
        
        else:
            raise Exception("No access token or authorization code provided")
        
    except Exception as e:
        print(f"\n[CRITICAL ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=f"Error fetching token: {str(e)}")

# --- GMAIL SERVICE ---
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

# --- EMAIL OPERATIONS ---
@app.get("/emails/recent")
def read_recent_emails(user_id: str = "user_123", max_results: int = 5):
    """Fetches recent emails and caches them for context."""
    service = get_gmail_service(user_id)
    try:
        results = service.users().messages().list(userId='me', labelIds=['INBOX'], maxResults=max_results).execute()
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
        
        # Cache emails for context
        cache_emails(user_id, email_summaries)
        
        return email_summaries
    except HttpError as error:
        raise HTTPException(status_code=500, detail=f"An error occurred with the Gmail API: {error}")

# --- AI REPLY GENERATION ---
@app.post("/emails/generate-reply")
def generate_ai_response(email_data: EmailContent, user_id: str = "user_123"):
    """Generates an AI reply with conversation context."""
    try:
        print("\n========== GENERATING AI REPLY ==========")
        
        api_key = os.getenv("MISTRAL_API_KEY")
        model = os.getenv("MISTRAL_MODEL", "mistral-small")
        if not api_key:
            raise Exception("MISTRAL_API_KEY not set in environment")

        endpoint = os.getenv("MISTRAL_API_URL", "https://api.mistral.ai/v1/chat/completions")
        
        # Include conversation context
        context = get_conversation_context(user_id, last_n=3)
        
        system_prompt = """You are a professional email assistant. Write clear, concise, and context-aware replies.
Consider the conversation history and maintain consistency in tone and style.
Your replies should be professional, helpful, and ready to send."""

        user_prompt = f"""{context}

Based on this email content, write a professional reply:

{email_data.content}

Generate a reply that is appropriate, professional, and addresses the key points."""

        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 200
        }

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        resp = requests.post(endpoint, headers=headers, json=payload, timeout=30)
        
        if resp.status_code != 200:
            fallback = """Thank you for your email. I've reviewed your message and will get back to you with a detailed response shortly.

Best regards"""
            return {"reply": fallback}

        data = resp.json()
        reply_text = None
        
        if isinstance(data, dict):
            choices = data.get("choices")
            if choices and isinstance(choices, list):
                first = choices[0]
                if isinstance(first, dict):
                    msg = first.get("message") or first.get("delta")
                    if isinstance(msg, dict):
                        reply_text = msg.get("content") or msg.get("text")

        reply_text = (reply_text or "").strip()
        
        print(f"[SUCCESS] Generated reply")
        return {"reply": reply_text}
        
    except Exception as e:
        print(f"\n[ERROR] AI generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error with AI: {str(e)}")

# --- DELETE EMAIL ---
@app.post("/emails/delete")
def delete_email(message: MessageId, user_id: str = "user_123"):
    """Deletes a specific email by its message ID."""
    service = get_gmail_service(user_id)
    try:
        service.users().messages().trash(userId='me', id=message.message_id).execute()
        add_to_conversation(user_id, "assistant", f"Email deleted successfully.", "delete_email")
        return {"status": "success", "message": f"Email with ID {message.message_id} moved to trash."}
    except HttpError as error:
        raise HTTPException(status_code=500, detail=f"Failed to delete email: {error}")

# --- ENHANCED CHATBOT COMMAND PROCESSOR ---
@app.post("/chatbot/command")
def process_chatbot_command(request: ChatCommand, user_id: str = "user_123"):
    """
    Enhanced chatbot with context awareness and better intent understanding.
    """
    command = request.command.strip()
    
    # Add user message to conversation
    add_to_conversation(user_id, "user", command)
    
    # Detect intent and extract entities
    analysis = detect_intent_and_entities(command, user_id)
    intent = analysis["intent"]
    entities = analysis["entities"]
    
    print(f"[DEBUG] Detected Intent: {intent}, Entities: {entities}")
    
    service = get_gmail_service(user_id)
    
    try:
        # Handle greetings
        if intent == "greet":
            response = "Hello! How can I help you with your emails today?"
            add_to_conversation(user_id, "assistant", response)
            return {"reply": response}
        
        # Handle help requests
        if intent == "help":
            response = generate_help_message()
            add_to_conversation(user_id, "assistant", response)
            return {"reply": response}
        
        # Handle status requests
        if intent == "status":
            last_action = get_last_action(user_id)
            if last_action:
                response = f"The last action I performed was: {last_action}"
            else:
                response = "I haven't performed any actions yet. How can I help you?"
            add_to_conversation(user_id, "assistant", response)
            return {"reply": response}
        
        # Handle fetch/read emails
        if intent == "fetch_emails":
            count = entities.get("count", 5)
            sender = entities.get("sender")
            
            if sender:
                query = f"from:{sender}"
                results = service.users().messages().list(userId='me', q=query, maxResults=count).execute()
                messages = results.get('messages', [])
                
                if not messages:
                    response = f"I couldn't find any emails from '{sender}'."
                    add_to_conversation(user_id, "assistant", response)
                    return {"reply": response}
                
                # Fetch and format emails
                email_list = []
                for msg_stub in messages:
                    msg = service.users().messages().get(userId='me', id=msg_stub['id']).execute()
                    headers = {h['name']: h['value'] for h in msg['payload']['headers']}
                    email_list.append({
                        "id": msg['id'],
                        "sender": headers.get('From', 'Unknown'),
                        "subject": headers.get('Subject', 'No Subject'),
                        "snippet": msg.get('snippet', '')
                    })
                
                cache_emails(user_id, email_list)
                
                response = f"Found {len(email_list)} email(s) from '{sender}':\n\n"
                for i, email in enumerate(email_list, 1):
                    response += f"{i}. **{email['subject']}**\n   From: {email['sender']}\n   {email['snippet'][:100]}...\n\n"
                
                add_to_conversation(user_id, "assistant", response, "fetch_emails")
                return {"reply": response}
            
            else:
                # Fetch recent emails
                results = service.users().messages().list(userId='me', labelIds=['INBOX'], maxResults=count).execute()
                messages = results.get('messages', [])
                
                email_list = []
                for msg_stub in messages:
                    msg = service.users().messages().get(userId='me', id=msg_stub['id']).execute()
                    headers = {h['name']: h['value'] for h in msg['payload']['headers']}
                    email_list.append({
                        "id": msg['id'],
                        "sender": headers.get('From', 'Unknown'),
                        "subject": headers.get('Subject', 'No Subject'),
                        "snippet": msg.get('snippet', '')
                    })
                
                cache_emails(user_id, email_list)
                
                response = f"Here are your latest {len(email_list)} emails:\n\n"
                for i, email in enumerate(email_list, 1):
                    response += f"{i}. **{email['subject']}**\n   From: {email['sender']}\n   {email['snippet'][:100]}...\n\n"
                
                add_to_conversation(user_id, "assistant", response, "fetch_emails")
                return {"reply": response}
        
        # Handle delete requests
        if intent == "delete_email":
            sender = entities.get("sender")
            email_ref = entities.get("email_reference")
            
            if sender:
                # Delete by sender
                results = service.users().messages().list(userId='me', q=f"from:{sender}", maxResults=1).execute()
                messages = results.get('messages', [])
                
                if not messages:
                    response = f"I couldn't find any emails from '{sender}'."
                    add_to_conversation(user_id, "assistant", response)
                    return {"reply": response}
                
                message_id = messages[0]['id']
                service.users().messages().trash(userId='me', id=message_id).execute()
                response = f"I've deleted the latest email from '{sender}'."
                add_to_conversation(user_id, "assistant", response, "delete_email")
                return {"reply": response}
            
            elif email_ref:
                # Delete by reference (this, that, first, etc.)
                email = find_email_by_reference(user_id, email_ref)
                
                if not email:
                    response = "I couldn't identify which email you want to delete. Could you be more specific?"
                    add_to_conversation(user_id, "assistant", response)
                    return {"reply": response}
                
                service.users().messages().trash(userId='me', id=email['id']).execute()
                response = f"I've deleted the email '{email['subject']}' from {email['sender']}."
                add_to_conversation(user_id, "assistant", response, "delete_email")
                return {"reply": response}
            
            else:
                response = "Please specify which email you want to delete. For example: 'delete the email from Amazon' or 'delete the first email'."
                add_to_conversation(user_id, "assistant", response)
                return {"reply": response}
        
        # Handle generate reply
        if intent == "generate_reply":
            email_ref = entities.get("email_reference") or command
            email = find_email_by_reference(user_id, email_ref)
            
            if not email:
                response = "Please fetch emails first, then I can help you draft a reply."
                add_to_conversation(user_id, "assistant", response)
                return {"reply": response}
            
            response = f"I'll draft a reply for the email '{email['subject']}'. Please use the 'Generate Reply' button on the email."
            add_to_conversation(user_id, "assistant", response, "generate_reply")
            return {"reply": response}
        
        # Default fallback with suggestions
        response = """I'm not sure I understood that correctly. Here are some things you can ask me:

• "Show me my latest 5 emails"
• "Read emails from john@example.com"
• "Delete the email from newsletter"
• "Help me reply to the first email"

What would you like to do?"""
        
        add_to_conversation(user_id, "assistant", response)
        return {"reply": response}
        
    except HttpError as error:
        response = f"I encountered an error: {str(error)}. Please try again."
        add_to_conversation(user_id, "assistant", response)
        return {"reply": response}
    except Exception as e:
        response = f"Something went wrong: {str(e)}. Please try again."
        add_to_conversation(user_id, "assistant", response)
        return {"reply": response}

# --- SEND EMAIL REPLY ---
@app.post("/emails/send")
def send_email_reply(payload: SendRequest, user_id: str = "user_123"):
    """Sends a reply to the original email."""
    service = get_gmail_service(user_id)
    try:
        original = service.users().messages().get(userId='me', id=payload.message_id, format='full').execute()
        headers = {h['name']: h['value'] for h in original.get('payload', {}).get('headers', [])}

        orig_from = headers.get('From', '')
        orig_subject = headers.get('Subject', '')
        orig_message_id = headers.get('Message-ID') or headers.get('Message-Id')

        _, from_email = parseaddr(orig_from)
        if not from_email:
            raise HTTPException(status_code=400, detail="Unable to determine recipient")

        reply_subject = orig_subject if orig_subject.lower().startswith('re:') else f"Re: {orig_subject}"

        msg = MIMEMultipart()
        msg['To'] = from_email
        msg['Subject'] = reply_subject
        if orig_message_id:
            msg['In-Reply-To'] = orig_message_id
            msg['References'] = orig_message_id

        body = MIMEText(payload.reply_text, 'plain')
        msg.attach(body)

        raw_bytes = base64.urlsafe_b64encode(msg.as_bytes())
        raw_str = raw_bytes.decode('utf-8')

        send_response = service.users().messages().send(userId='me', body={'raw': raw_str}).execute()
        
        add_to_conversation(user_id, "assistant", f"Email sent successfully to {from_email}.", "send_email")

        return {"status": "sent", "gmail_message_id": send_response.get('id')}

    except HttpError as error:
        raise HTTPException(status_code=500, detail=f"Failed to send reply: {error}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- CONVERSATION HISTORY ENDPOINT ---
@app.get("/chatbot/history")
def get_conversation_history(user_id: str = "user_123"):
    """Get the conversation history for a user."""
    if user_id not in conversation_memory:
        return {"history": []}
    return {"history": conversation_memory[user_id]}

# --- CLEAR CONVERSATION ---
@app.post("/chatbot/clear")
def clear_conversation(user_id: str = "user_123"):
    """Clear conversation history for a user."""
    if user_id in conversation_memory:
        conversation_memory[user_id] = []
    if user_id in email_cache:
        email_cache[user_id] = {"emails": [], "timestamp": ""}
    return {"status": "cleared"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)