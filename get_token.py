
import subprocess
import re
import sys

def get_access_token():
    """Gets the access token by running the Twitch CLI."""
    try:
        print("Attempting to get a new access token. Please follow the instructions in your browser.")
        command = ["twitch", "token", "-u", "-s", "user:read:follows"]
        # We don't check for success because the token is often printed to stderr on success
        result = subprocess.run(command, capture_output=True, text=True)
        
        # The token can be in stdout or stderr, so we check both
        output = result.stderr + result.stdout
        
        match = re.search(r"User Access Token: (\w+)", output)
        if match:
            return match.group(1)
        else:
            print("Could not get access token from the Twitch CLI output.")
            print("--- Full Output ---")
            print(output)
            print("---------------------")
            return None
            
    except FileNotFoundError:
        print("Twitch CLI not found. Please make sure it is installed and in your PATH.")
        return None
    except Exception as e:
        print(f"An unexpected error occurred while getting the access token: {e}")
        return None

if __name__ == "__main__":
    access_token = get_access_token()
    if access_token:
        print("\nAccess token found:")
        print(access_token)
