import requests
import os
import random
from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip
from content_gen import ContentGenerator
import PIL.Image

# Monkeypatch for older moviepy + newer pillow
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.LANCZOS

class VideoReelGenerator:
    def __init__(self):
        self.content_gen = ContentGenerator()
        self.pexels_key = os.getenv("PEXELS_API_KEY")
        self.pixabay_key = os.getenv("PIXABAY_API_KEY")

    def get_pexels_video(self, query):
        if not self.pexels_key: return None
        headers = {"Authorization": self.pexels_key}
        url = f"https://api.pexels.com/videos/search?query={query}&per_page=5&orientation=portrait"
        try:
            res = requests.get(url, headers=headers, timeout=15)
            if res.status_code == 200:
                videos = res.json().get("videos", [])
                if videos:
                    v = random.choice(videos)
                    files = sorted(v.get("video_files", []), key=lambda x: x.get("width", 0), reverse=True)
                    for f in files:
                        if 720 <= f.get("width") <= 1080: return f.get("link")
                    return files[0].get("link")
        except: pass
        return None

    def get_pixabay_video(self, query):
        if not self.pixabay_key: return None
        url = f"https://pixabay.com/api/videos/?key={self.pixabay_key}&q={query}&video_type=film&per_page=5"
        try:
            res = requests.get(url, timeout=15)
            if res.status_code == 200:
                hits = res.json().get("hits", [])
                if hits:
                    v = random.choice(hits)
                    # Pick large resolution
                    return v.get("videos", {}).get("large", {}).get("url") or v.get("videos", {}).get("medium", {}).get("url")
        except: pass
        return None

    def download_video(self, url):
        path = "temp_stock.mp4"
        try:
            res = requests.get(url, stream=True, timeout=30)
            with open(path, "wb") as f:
                for chunk in res.iter_content(1024):
                    if chunk: f.write(chunk)
            return path
        except: return None

    def create_reel(self):
        print("Generating Pro Stock Reel...")
        fact, img_prompt = self.content_gen.generate_text()
        if not fact: return None, None

        # Try multiple sources and queries for variety
        sources = [
            (self.get_pexels_video, img_prompt),
            (self.get_pixabay_video, img_prompt),
            (self.get_pexels_video, self.content_gen.niche),
            (self.get_pixabay_video, self.content_gen.niche)
        ]
        
        video_url = None
        for func, query in sources:
            video_url = func(query)
            if video_url: break
            
        if not video_url:
            print("Action Failed: No stock video found. Check your API keys and Internet.")
            return None, None

        temp_vid = self.download_video(video_url)
        if not temp_vid: return None, None

        try:
            clip = VideoFileClip(temp_vid)
            duration = min(clip.duration, 10)
            clip = clip.subclip(0, duration)
            
            # Simple text overlay logic
            frame = clip.get_frame(0)
            pil_frame = PIL.Image.fromarray(frame)
            final_img = self.content_gen.overlay_text(pil_frame, fact)
            overlay_path = "temp_overlay.png"
            final_img.save(overlay_path)
            
            overlay_clip = (ImageClip(overlay_path)
                           .set_duration(duration)
                           .set_position("center"))
            
            # Final export
            final_video = CompositeVideoClip([clip, overlay_clip])
            output_file = "temp_reel_stock.mp4"
            final_video.write_videofile(output_file, codec="libx264", audio=False, fps=24)
            
            clip.close()
            final_video.close()
            
            if os.path.exists(temp_vid): os.remove(temp_vid)
            if os.path.exists(overlay_path): os.remove(overlay_path)
            
            return output_file, fact
        except Exception as e:
            print(f"Error: {e}")
            return None, None

if __name__ == "__main__":
    vg = VideoReelGenerator()
    # Mocking for local test if API fails
    try:
        file, caption = vg.create_reel()
    except:
        print("API failed, using mock content for visual test...")
        vg.content_gen.generate_text = lambda: ("The ocean contains enough gold to provide every person on Earth with nine pounds of it.", "Ocean gold treasure")
        file, caption = vg.create_reel()
        
    if file:
        print(f"Stock Reel created: {file}")
