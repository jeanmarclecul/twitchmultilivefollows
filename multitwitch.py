
import requests
import webbrowser
import json
import sys

def get_user_id(client_id, access_token):
    """Gets the user ID from the Twitch API."""
    try:
        headers = {
            "Client-ID": client_id,
            "Authorization": f"Bearer {access_token}",
        }
        url = "https://api.twitch.tv/helix/users"
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        if data.get("data"):
            return data["data"][0]["id"]
        else:
            print("Could not get user ID. The access token might be invalid.")
            return None
    except requests.exceptions.HTTPError as err:
        print(f"An error occurred while getting the user ID: {err}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred while getting the user ID: {e}")
        return None

def get_followed_channels(client_id, user_id, access_token):
    """Gets the list of followed channels from the Twitch API."""
    headers = {
        "Client-ID": client_id,
        "Authorization": f"Bearer {access_token}",
    }
    
    followed_channels = []
    cursor = None
    
    while True:
        url = f"https://api.twitch.tv/helix/channels/followed?user_id={user_id}"
        if cursor:
            url += f"&after={cursor}"
            
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        
        followed_channels.extend(data.get("data", []))
        
        pagination = data.get("pagination", {})
        cursor = pagination.get("cursor")
        
        if not cursor:
            break
            
    return followed_channels

def get_live_channels(client_id, access_token, followed_channels):
    """Gets the list of live channels from a list of followed channels."""
    if not followed_channels:
        return []

    headers = {
        "Client-ID": client_id,
        "Authorization": f"Bearer {access_token}",
    }
    
    live_channels = []
    user_ids = [channel["broadcaster_id"] for channel in followed_channels]
    
    # The /helix/streams endpoint can take up to 100 user IDs at a time.
    chunk_size = 100
    for i in range(0, len(user_ids), chunk_size):
        user_id_chunk = user_ids[i:i + chunk_size]
        url = "https://api.twitch.tv/helix/streams?user_id=" + "&user_id=".join(user_id_chunk)
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        live_channels.extend([stream["user_login"] for stream in data.get("data", [])])
        
    return live_channels

def main():
    """Main function to get followed channels and open MultiTwitch."""
    print("Twitch MultiTwitch URL Generator")
    print("--------------------------------")
    
    if len(sys.argv) < 3:
        print("Usage: python multitwitch.py <client_id> <access_token>")
        return

    client_id = sys.argv[1]
    access_token = sys.argv[2]
    
    user_id = get_user_id(client_id, access_token)
    if not user_id:
        return
        
    try:
        print("Getting your followed channels...")
        followed_channels = get_followed_channels(client_id, user_id, access_token)
        
        if not followed_channels:
            print("You are not following any channels.")
            return

        print("Checking which channels are live...")
        live_channels = get_live_channels(client_id, access_token, followed_channels)
        
        if not live_channels:
            print("None of your followed channels are currently live.")
            return
            
        multitwitch_url = "https://www.multitwitch.tv/" + "/".join(live_channels)
        
        print("Opening the MultiTwitch URL with live channels in your browser...")
        webbrowser.open(multitwitch_url)
        
        print("Done!")
        
    except requests.exceptions.HTTPError as err:
        print(f"An error occurred: {err}")
    except Exception as err:
        print(f"An unexpected error occurred: {err}")

if __name__ == "__main__":
    main()
