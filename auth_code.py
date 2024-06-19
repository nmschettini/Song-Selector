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

if __name__ == "__main__":
    import os
    from dotenv import load_dotenv

    load_dotenv()
    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")

    get_code()