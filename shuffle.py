import random
from spotify_util import SpotifyAuth, SpotifyApp

def shuffle(sp: SpotifyApp, source: str, dest: str, count: int = 50) -> None:
    source_id = sp.get_playlist_id(source)
    if not source_id:
        raise Exception(f'No playlist named "{source}".')
    dest_id = sp.get_playlist_id(dest)
    if not dest_id:
        raise Exception(f'No playlist named "{dest}".')
    
    songs = sp.get_playlist_songs(source_id)
    uris = [song["uri"] for song in songs]

    sp.clear_playlist(dest_id)

    sp.add_to_playlist(dest_id, random.sample(uris, count))

if __name__ == "__main__":
    import os
    from dotenv import load_dotenv

    load_dotenv()
    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")
    source_name = os.getenv("SOURCE_PLAYLIST")
    destination_name = os.getenv("DESTINATION_PLAYLIST")
    
    auth = SpotifyAuth(client_id, 
                       client_secret, 
                       "playlist-read-private playlist-modify-public playlist-modify-private",
                       "http://localhost:5000/callback")

    if os.path.isfile("auth_response.json"):
        auth.read_token("auth_response.json")
    else:
        code = auth.get_code_manual()
        auth.get_token(code)
    
    sp = SpotifyApp(auth)

    shuffle(sp, source_name, destination_name)

    auth.write_token("auth_response.json")