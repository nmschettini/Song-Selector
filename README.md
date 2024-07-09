# Spotify Song Selector
## Description
This is a script that interacts with the Spotify API. It takes 50 songs from a source playlists and places them into the destination playlist. Currently, the script will delete all other songs in the destination playlist.

## Requirements
- requests
- python-dotenv

## Instructions
1. Create a Spotify app at https://developer.spotify.com/dashboard
2. Set the redirect uri of that app to be http://localhost:5000/callback (or change the redirect uri in shuffle.py)
3. Replace the values in the .env file for CLIENT_ID, and CLIENT_SECRET. CLIENT_ID and CLIENT_SECRET come from the spotify for developers dashboard.
4. Run the script by doing "py shuffle.py" in your command prompt
5. If it is your first time running the script, a tab in your web browser will open up. Follow the instructions and copy the link you get redirected to into the command prompt.
