from instagrapi import Client
import os
from dotenv import load_dotenv

load_dotenv()

cl = Client()
username = os.getenv("IG_USERNAME")
password = os.getenv("IG_PASSWORD")

try:
    if os.path.exists("ig_session.json"):
        cl.load_settings("ig_session.json")
    cl.login(username, password)
    
    user_id = cl.user_id_from_username(username)
    medias = cl.user_medias(user_id, amount=5)
    
    print(f"Recent posts for {username}:")
    for media in medias:
        print(f"- ID: {media.pk}, Type: {media.media_type}, Caption: {media.caption_text[:50]}...")
except Exception as e:
    print(f"Failed to check posts: {e}")
