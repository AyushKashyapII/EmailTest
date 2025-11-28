"""
Instructions to properly set up Google OAuth:

1. Go to https://console.cloud.google.com/
2. Select your project
3. Go to APIs & Services > Credentials
4. Find your OAuth 2.0 Client (Web application)
5. Click the download button (down arrow) - this will download the actual client_secret.json
6. Replace the client_secret.json in this backend directory with the downloaded file

IMPORTANT: The client_secret.json from Google will have this structure:
{
  "web": {
    "client_id": "YOUR_CLIENT_ID.apps.googleusercontent.com",
    "project_id": "YOUR_PROJECT_ID",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_secret": "YOUR_CLIENT_SECRET",
    "redirect_uris": ["http://localhost:5173/"],
    "javascript_origins": ["http://localhost:5173"]
  }
}

Note: It uses "web" key, not "installed" for web applications.
"""
