
import subprocess
import re
import sys
import os
import webbrowser
import http.server
import socketserver
import threading
import urllib.parse
from dotenv import load_dotenv

class OAuthHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        query = urllib.parse.urlparse(self.path).query
        params = urllib.parse.parse_qs(query)
        
        if 'code' in params:
            self.server.auth_code = params['code'][0]
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"<h1>Authorization successful! You can close this window.</h1>")
        else:
            self.send_response(400)
            self.end_headers()

def get_access_token():
    """Gets the access token using Twitch OAuth flow."""
    try:
        load_dotenv()
        
        client_id = os.getenv("CLIENT_ID")
        client_secret = os.getenv("SECRET_ID")
        
        if not client_id or not client_secret:
            print("CLIENT_ID or SECRET_ID not found in .env file.")
            return None
        
        # Start local server for OAuth callback
        PORT = 3000
        handler = OAuthHandler
        handler.server = None
        
        with socketserver.TCPServer(("", PORT), handler) as httpd:
            handler.server = httpd
            httpd.auth_code = None
            
            # OAuth URL
            auth_url = f"https://id.twitch.tv/oauth2/authorize?client_id={client_id}&redirect_uri=http://localhost:{PORT}&response_type=code&scope=user:read:follows"
            
            print(f"Opening browser for authorization...")
            webbrowser.open(auth_url)
            
            # Wait for callback (timeout after 2 minutes)
            httpd.timeout = 120
            httpd.handle_request()
            
            if not hasattr(httpd, 'auth_code') or not httpd.auth_code:
                print("Authorization timed out or failed.")
                return None
            
            # Exchange code for token
            import requests
            token_url = "https://id.twitch.tv/oauth2/token"
            data = {
                "client_id": client_id,
                "client_secret": client_secret,
                "code": httpd.auth_code,
                "grant_type": "authorization_code",
                "redirect_uri": f"http://localhost:{PORT}"
            }
            
            response = requests.post(token_url, data=data)
            if response.status_code == 200:
                return response.json().get("access_token")
            else:
                print(f"Failed to get token: {response.text}")
                return None
                
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

if __name__ == "__main__":
    access_token = get_access_token()
    if access_token:
        print("\nAccess token found:")
        print(access_token)
        with open(".token", "w") as f:
            f.write(access_token)
        print("Access token stored in .token file.")
