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
        self.session_file = "ig_session.json"

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
            return media
        except Exception as e:
            print(f"Upload failed: {e}")
            return None

    def prepare_video_for_instagram(self, video_path):
        """Re-encode video to Instagram-exact specs to preserve audio."""
        output = "temp_ig_ready.mp4"
        try:
            cmd = [
                "ffmpeg", "-y", "-i", video_path,
                "-c:v", "libx264",        # H.264 video
                "-preset", "fast",
                "-crf", "23",
                "-c:a", "aac",            # AAC audio
                "-b:a", "128k",           # 128kbps bitrate (Instagram standard)
                "-ar", "44100",           # 44100 Hz sample rate
                "-ac", "2",              # Stereo
                "-movflags", "+faststart", # moov atom at front (critical for Instagram)
                "-pix_fmt", "yuv420p",    # Required pixel format
                "-r", "30",              # 30 fps
                output
            ]
            print("Re-encoding video for Instagram compatibility...")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            if result.returncode == 0 and os.path.exists(output):
                print(f"Video re-encoded successfully ({os.path.getsize(output)/1024/1024:.1f} MB)")
                if os.path.exists(video_path): os.remove(video_path)
                return output
            else:
                print(f"FFmpeg error: {result.stderr[:200]}")
        except FileNotFoundError:
            print("FFmpeg not found locally, using original video.")
        except Exception as e:
            print(f"Re-encode failed: {e}")
        return video_path

    def post_reel(self, video_path, caption):
        print(f"Uploading reel with caption: {caption[:80]}...")
        try:
            # Re-encode for Instagram compatibility
            video_path = self.prepare_video_for_instagram(video_path)
            time.sleep(random.randint(3, 8))
            # video_upload posts legacy videos, which IG automatically converts to Reels
            # This often bypasses the audio-stripping bug present in clip_upload
            media = self.cl.video_upload(video_path, caption)
            print("Reel upload successful!")
            return media
        except Exception as e:
            print(f"Reel upload failed: {e}")
            return None

if __name__ == "__main__":
    # Test Login
    mgr = InstaManager()
    mgr.login()
