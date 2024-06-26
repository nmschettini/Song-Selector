import os, json
from dotenv import load_dotenv
from spotify_token import get_token, refresh_token

load_dotenv()
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
source_name = os.getenv("SOURCE_PLAYLIST")
destination_name = os.getenv("DESTINATION_PLAYLIST")

def get_playlist_id(name: str) -> str | None:
    from requests import get

    url = "https://api.spotify.com/v1/me/playlists"

    header = {
        "Authorization": f"Bearer {get_token()}"
    }

    response = get(url, headers=header)
    json_response = json.loads(response.content)

    playlists = None
    try:
        playlists = json_response["items"]
    except:
        header["Authorization"] = f"Bearer {refresh_token()}"
        response = get(url, headers=header)
        json_response = json.loads(response.content)

        playlists = json_response["items"]
    
    for playlist in playlists:
        if playlist["name"] == name:
            return playlist["id"]
    
    return None

def get_playlist_info(id: str) -> dict:
    from requests import get

    url = f"https://api.spotify.com/v1/playlists/{id}"

    header = {
        "Authorization": f"Bearer {get_token()}"
    }

    response = get(url, headers=header)
    json_response = json.loads(response.content)

    try:
        json_response["id"]
    except:
        header["Authorization"] = f"Bearer {refresh_token()}"
        response = get(url, headers=header)
        json_response = json.loads(response.content)
    
    return json_response

def get_playlist_songs(id: str) -> list:
    items = get_playlist_info(id)["tracks"]["items"]

    songs = []
    for item in items:
        songs.append(item["track"])

    return songs

def clear_playlist(id: str) -> None:
    from requests import delete
    
    url = f"https://api.spotify.com/v1/playlists/{id}/tracks"

    songs = get_playlist_songs(id)
    uris = [song["uri"] for song in songs]
    snapshot_id = get_playlist_info(id)["snapshot_id"]

    headers = {
        "Authorization": f"Bearer {get_token()}",
        "Content-Type": "application/json"
    }

    data = {
        "tracks": [{"uri": uri} for uri in uris],
        "snapshot_id": snapshot_id
    }
    data = json.dumps(data)

    response = delete(url, headers=headers, data=data)
    json_response = json.loads(response.content)

    try:
        json_response["snapshot_id"]
    except:
        headers["Authorization"] = f"Bearer {refresh_token()}"
        delete(url, headers=headers, data=data)

def add_to_playlist(id: str, song_uris: list[str]) -> None:
    if len(song_uris) > 100:
        raise Exception("Can only add upto 100 songs at a time.")
    
    from requests import post

    url = f"https://api.spotify.com/v1/playlists/{id}/tracks"

    headers = {
        "Authorization": f"Bearer {get_token()}",
        "Content-Type": "application/json"
    }

    data = {
        "uris": song_uris
    }
    data = json.dumps(data)

    response = post(url, headers=headers, data=data)
    json_response = json.loads(response.content)

    try:
        json_response["snapshot_id"]
    except:
        headers["Authorization"] = f"Bearer {refresh_token()}"
        post(url, headers=headers, data=data)


def shuffle(source: str, dest: str, count: int = 50) -> None:
    import random

    source_id = get_playlist_id(source)
    if not source_id:
        raise Exception(f'No playlist named "{source}".')
    dest_id = get_playlist_id(dest)
    if not dest_id:
        raise Exception(f'No playlist named "{dest}".')
    
    songs = get_playlist_songs(source_id)
    uris = [song["uri"] for song in songs]

    clear_playlist(dest_id)

    add_to_playlist(dest_id, random.sample(uris, count))

if __name__ == "__main__":
    shuffle(source_name, destination_name)