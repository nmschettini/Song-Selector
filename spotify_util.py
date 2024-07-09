import json, time, secrets, webbrowser, re, os
from requests import post, get, delete
from urllib.parse import urlencode
from base64 import b64encode

class SpotifyAuth:
    def __init__(self, client_id: str, client_secret: str, scope: str, redirect_uri: str) -> None:
        self.client_id = client_id
        self.client_secret = client_secret
        self.scope = scope
        self.redirect_uri = redirect_uri

        self.token_info = None
        self.token_expire_time = None

    def get_auth_url(self) -> str:
        state = secrets.token_urlsafe(16)

        headers = {
            "response_type": "code",
            "client_id": self.client_id,
            "scope": self.scope,
            "redirect_uri": self.redirect_uri,
            "state": state
        }

        url = "https://accounts.spotify.com/authorize?"
        query_url = url + urlencode(headers)

        return query_url
        
    @staticmethod
    def parse_code(redirect_result_url: str) -> str:
        return re.sub(".*code=|&(.*)", "", redirect_result_url)
    
    def get_code_manual(self) -> str:
        url = self.get_auth_url()
        webbrowser.open_new_tab(url)

        redirect = str(input("Please input the url of the tab opened:\n"))

        return self.parse_code(redirect)
    
    def __auth_encode(self) -> str:
        auth_string = self.client_id + ":" + self.client_secret
        auth_bytes = auth_string.encode("utf-8")
        return str(b64encode(auth_bytes), "utf-8")
    
    def get_token(self, code: str) -> dict:
        url = "https://accounts.spotify.com/api/token"
        
        auth_base64 = self.__auth_encode()
        headers = {
            "Authorization": "Basic " + auth_base64,
            "Content-Type": "application/x-www-form-urlencoded"
        }

        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.redirect_uri
        }

        response = post(url, headers=headers, data=data)

        self.token_info = json.loads(response.content)
        self.token_expire_time = self.token_info["expires_in"] + time.time()
        
        return self.token_info
    
    def read_token(self, file_path: str) -> dict | None:
        if os.path.isfile(file_path):
            with open(file_path, "r") as infile:
                self.token_info = json.load(infile)
        
        return self.token_info
    
    def write_token(self, file_path: dict) -> None:
        with open(file_path, "w") as outfile:
            json.dump(self.token_info, outfile)

    def is_token_expired(self) -> bool:
        if not self.token_expire_time:
            return True

        if time.time() >= self.token_expire_time - 60:
            return True
        
        return False

    def refresh_token(self) -> dict:
        url = "https://accounts.spotify.com/api/token"
        
        auth_base64 = self.__auth_encode()
        
        headers = {
            "Authorization": "Basic " + auth_base64,
            "Content-Type": "application/x-www-form-urlencoded"
        }

        data = {
            "grant_type": "refresh_token",
            "refresh_token": self.token_info["refresh_token"]
        }

        response = post(url, headers=headers, data=data)
        json_response = json.loads(response.content)

        json_response["refresh_token"] = self.token_info["refresh_token"]
        
        self.token_info = json_response
        self.token_expire_time = self.token_info["expires_in"] + time.time()

        return self.token_info


class SpotifyApp:
    def __init__(self, auth: SpotifyAuth) -> None:
        if not auth.token_info:
            raise Exception("Proved auth object has no existing token.")
        self.auth = auth

    def get_access_token(self):
        if self.auth.is_token_expired():
            self.auth.refresh_token()

        return self.auth.token_info["access_token"]

    def get_playlist_id(self, name: str) -> str | None:
        url = "https://api.spotify.com/v1/me/playlists"

        header = {
            "Authorization": f"Bearer {self.get_access_token()}"
        }

        response = get(url, headers=header)

        playlists = json.loads(response.content)["items"]
        for playlist in playlists:
            if playlist["name"] == name:
                return playlist["id"]
        
        return None
    
    def get_playlist_info(self, id: str) -> dict:
        url = f"https://api.spotify.com/v1/playlists/{id}"

        header = {
            "Authorization": f"Bearer {self.get_access_token()}"
        }

        response = get(url, headers=header)

        return json.loads(response.content)
    
    def get_playlist_songs(self, id: str) -> list:
        items = self.get_playlist_info(id)["tracks"]["items"]

        songs = []
        for item in items:
            songs.append(item["track"])

        return songs
    
    def clear_playlist(self, id: str) -> None:
        url = f"https://api.spotify.com/v1/playlists/{id}/tracks"

        songs = self.get_playlist_songs(id)
        uris = [song["uri"] for song in songs]
        snapshot_id = self.get_playlist_info(id)["snapshot_id"]

        headers = {
            "Authorization": f"Bearer {self.get_access_token()}",
            "Content-Type": "application/json"
        }

        data = {
            "tracks": [{"uri": uri} for uri in uris],
            "snapshot_id": snapshot_id
        }
        data = json.dumps(data)

        delete(url, headers=headers, data=data)

    def add_to_playlist(self, id: str, song_uris: list[str]) -> None:
        if len(song_uris) > 100:
            raise Exception("Can only add upto 100 songs at a time.")
        
        url = f"https://api.spotify.com/v1/playlists/{id}/tracks"

        headers = {
            "Authorization": f"Bearer {self.get_access_token()}",
            "Content-Type": "application/json"
        }

        data = {
            "uris": song_uris
        }
        data = json.dumps(data)

        post(url, headers=headers, data=data)
