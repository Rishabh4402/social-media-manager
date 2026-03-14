from instagrapi import Client
import os
import subprocess
from dotenv import load_dotenv
import time
import random

load_dotenv()

class InstaManager:
    def __init__(self):
        self.cl = Client()
        self.username = os.getenv("IG_USERNAME")
        self.password = os.getenv("IG_PASSWORD")
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.session_file = os.path.join(base_path, "ig_session.json")

    def login(self):
        print(f"Attempting login as {self.username}...")
        try:
            if os.path.exists(self.session_file):
                self.cl.load_settings(self.session_file)
                print("Loaded existing session.")
            
            self.cl.login(self.username, self.password)
            self.cl.dump_settings(self.session_file)
            print("Login successful.")
            return True
        except Exception as e:
            print(f"Login failed: {e}")
            return False

    def post_photo(self, photo_path, caption):
        print(f"Uploading photo with caption: {caption}")
        try:
            # Add a small delay to look human
            time.sleep(random.randint(5, 15))
            media = self.cl.photo_upload(photo_path, caption)
            print("Upload successful!")
        except Exception as e:
            print(f"Upload failed: {e}")
            return None

    def post_reel(self, video_path, caption):
        print(f"Uploading reel with caption: {caption[:80]}...")
        try:
            # Add a delay to look more human
            time.sleep(random.randint(3, 8))
            
            # Using clip_upload with explicit audio_muted=False
            # The faststart flag in trending_reels ensures the file can be parsed
            extra = {"audio_muted": False}
            media = self.cl.clip_upload(video_path, caption, extra_data=extra)
            print("Reel upload successful!")
            return media
        except Exception as e:
            print(f"Reel upload failed: {e}")
            return None

if __name__ == "__main__":
    # Test Login
    mgr = InstaManager()
    mgr.login()
