import os
from dotenv import load_dotenv
load_dotenv()
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

def get_code():
    from urllib.parse import urlencode
    import secrets, webbrowser

    state = secrets.token_urlsafe(16)
    scope = "playlist-read-private playlist-modify-public playlist-modify-private"

    headers = {
        "response_type": "code",
        "client_id": client_id,
        "scope": scope,
        "redirect_uri": "http://localhost:5000/callback",
        "state": state
    }

    url = "https://accounts.spotify.com/authorize?"
    query_url = url + urlencode(headers)

    webbrowser.open_new_tab(query_url)

def encode_authorization(client_id: str, client_secret: str) -> str:
    from base64 import b64encode
    auth_string = client_id + ":" + client_secret
    auth_bytes = auth_string.encode("utf-8")
    return str(b64encode(auth_bytes), "utf-8")

def get_auth_response() -> str:
    import json
    if os.path.isfile("auth_response.json"):
        with open("auth_response.json", "r") as infile:
            response = json.load(infile)
        return response
    
    from requests import post
    url = "https://accounts.spotify.com/api/token"
    
    auth_base64 = encode_authorization(client_id, client_secret)
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }

    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": "http://localhost:5000/callback"
    }

    response = post(url, headers=headers, data=data)
    json_response = json.loads(response.content)

    with open("auth_response.json", "w") as outfile:
        json.dump(json_response, outfile)
    
    return json_response

def get_token():
    return get_auth_response()["access_token"]

def refresh_token():
    import json
    from requests import post
    url = "https://accounts.spotify.com/api/token"

    auth_base64 = encode_authorization(client_id, client_secret)
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }

    refresh_token = get_auth_response()["refresh_token"]
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token
    }

    response = post(url, headers=headers, data=data)
    json_response = json.loads(response.content)

    json_response["refresh_token"] = refresh_token
    with open("auth_response.json", "w") as outfile:
        json.dump(json_response, outfile)
    
    return json_response["access_token"]

if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()
    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")

    get_code()
    try:
        code = input("Input the code provided in the redirect URI:\n")
        get_auth_response()
        print("Token obtained successfully.")
    except:
        print("Incorrect code input. Unable to get token.")
    
    