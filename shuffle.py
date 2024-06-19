import os
from dotenv import load_dotenv

load_dotenv()
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
source_name = os.getenv("SOURCE_PLAYLIST")
destination_name = os.getenv("DESTINATION_PLAYLIST")