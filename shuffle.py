import os
from dotenv import load_dotenv

load_dotenv()
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
auth_code = os.getenv("AUTH_CODE")
source_name = os.getenv("SOURCE_PLAYLIST")
destination_name = os.getenv("DESTINATION_PLAYLIST")

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
        "code": auth_code,
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