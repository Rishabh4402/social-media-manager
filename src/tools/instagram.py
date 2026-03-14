import pyotp
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
        self.two_factor_seed = os.getenv("IG_2FA_SEED")
        self.proxy = os.getenv("IG_PROXY")
        
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.session_file = os.path.join(base_path, "ig_session.json")
        
        if self.proxy:
            print(f"Using proxy: {self.proxy}")
            self.cl.set_proxy(self.proxy)

    def challenge_code_handler(self, username, choice):
        print(f"--- Instagram Challenge Required for {username} ---")
        print(f"A verification code was sent via {choice}")
        code = input("Please enter the verification code: ")
        return code

    def login(self):
        print(f"Attempting login as {self.username}...")
        self.cl.challenge_code_handler = self.challenge_code_handler
        
        # Prep 2FA code if seed is provided
        verification_code = None
        if self.two_factor_seed:
            try:
                totp = pyotp.TOTP(self.two_factor_seed.replace(" ", ""))
                verification_code = totp.now()
                print("Generated 2FA verification code automatically.")
            except Exception as e:
                print(f"Failed to generate 2FA code: {e}")

        try:
            if os.path.exists(self.session_file):
                self.cl.load_settings(self.session_file)
                print("Loaded existing session.")
            
            # Login with verification code if available
            self.cl.login(self.username, self.password, verification_code=verification_code)
            self.cl.dump_settings(self.session_file)
            print("Login successful.")
            return True
        except Exception as e:
            msg = str(e).lower()
            if "challenge_required" in msg:
                print("CRITICAL: Instagram requires a security challenge.")
                print("Please log in to your Instagram app on your phone and approve the login attempt.")
            elif "two_factor_required" in msg:
                print("CRITICAL: 2FA is required but automation failed.")
            print(f"Login failed: {e}")
            # If login fails, wipe the session file so the next attempt starts fresh
            if os.path.exists(self.session_file):
                print("Wiping session file to recover from potential corruption.")
                os.remove(self.session_file)
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
