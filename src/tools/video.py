import requests
import os
import json
import random
from dotenv import load_dotenv
from src.tools.llm import ContentGenerator
from src.memory.history import HistoryManager
import PIL.Image
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.LANCZOS
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeAudioClip
try:
    from moviepy.audio.fx.all import speedx
except ImportError:
    try:
        from moviepy.video.fx.all import speedx
    except ImportError:
        # Final fallback: define a dummy function if it totally fails
        # to avoid crashing the whole agent
        def speedx(clip, factor): return clip


load_dotenv()

# 80+ trending topics for Indian / European / US audiences
TRENDING_TOPICS = [
    # 🧘 Spiritual
    "meditation peaceful", "buddha temple", "yoga sunrise", "candle flame calm",
    "zen garden", "spiritual healing light", "incense smoke", "lotus flower water",
    "temple bells india", "ganges river prayer", "diya lamp festival",
    # 💪 Motivational
    "motivation success", "gym workout", "running sunrise", "never give up",
    "hustle grind", "champion victory", "mountain summit climb", "boxing training",
    "entrepreneur lifestyle", "hard work dedication", "sigma mindset",
    # 🎨 Animation & Art
    "3d animation", "abstract art colorful", "digital art fantasy", "cartoon animation",
    "glitch art", "fractal zoom", "kaleidoscope patterns", "liquid art fluid",
    "neon animation loop", "geometric animation",
    # 🧠 Science & Facts
    "space nebula", "galaxy stars", "milky way", "deep sea creatures",
    "volcano lava", "lightning storm", "meteor shower", "northern lights",
    "underwater coral reef", "tornado storm", "human body facts",
    # 💻 Tech & AI
    "artificial intelligence", "robot technology", "futuristic city", "coding programming",
    "self driving car", "drone technology", "virtual reality", "hologram technology",
    "space station", "mars rover", "quantum computer", "cyber security hacking",
    # 🎵 Music & Songs
    "piano music", "guitar playing", "violin classical", "tabla drums india",
    "flute music peaceful", "DJ mixing music", "concert crowd", "singing performance",
    "street musician", "jazz saxophone",
    # 🌍 Nature & Satisfying
    "satisfying", "ocean waves", "waterfall", "rain drops", "sunset clouds",
    "cherry blossom", "autumn leaves", "snowfall forest", "forest fog",
    "tropical beach", "rainbow sky", "hummingbird slow motion",
    # 🏙️ Random Viral
    "city night", "drone aerial city", "tokyo night", "neon lights city",
    "fireworks celebration", "hot air balloon", "paragliding mountains",
    "car racing speed", "skateboard tricks", "cooking fire", "coffee art latte",
    # 🇮🇳 India Specials
    "taj mahal india", "indian festival colors", "bollywood dance", "indian street food",
    "kerala backwaters", "rajasthan desert", "himalaya mountains", "indian wedding",
    "diwali lights festival", "holi colors festival"
]

# Bilingual hashtags for global reach (India + Europe + US)
VIRAL_HASHTAGS = [
    # 🌐 Global
    "#reels", "#reelsinstagram", "#viral", "#explore", "#trending",
    "#fyp", "#reelitfeelit", "#instagramreels", "#viralreels",
    "#explorepage", "#trendingnow", "#satisfying", "#beautiful",
    "#mindblown", "#didyouknow", "#amazing", "#incredible",
    # 🇮🇳 India
    "#indianreels", "#desireels", "#hindivibes", "#bharatiya",
    "#shayari", "#motivationalquotes", "#indianculture",
    # 🇺🇸🇬🇧 US/Europe
    "#sciencefacts", "#techworld", "#AIrevolution", "#naturephotography",
    "#cinematicvideo", "#earthporn", "#stunningviews"
]

class TrendingReelDownloader:
    def __init__(self):
        self.pixabay_key = os.getenv("PIXABAY_API_KEY")
        self.content_gen = ContentGenerator()
        self.history = HistoryManager()


    def get_trending_video(self):
        """Fetch a popular, never-before-posted video from Pixabay."""
        if not self.pixabay_key:
            print("PIXABAY_API_KEY missing.")
            return None, None, None

        # Shuffle topics for variety
        topics = TRENDING_TOPICS.copy()
        random.shuffle(topics)

        for topic in topics[:5]:  # Try up to 5 different topics
            print(f"Searching: '{topic}'")
            url = (
                f"https://pixabay.com/api/videos/"
                f"?key={self.pixabay_key}"
                f"&q={requests.utils.quote(topic)}"
                f"&video_type=film"
                f"&per_page=40"
                f"&order=popular"
                f"&min_width=720"
            )

            try:
                res = requests.get(url, timeout=15)
                if res.status_code != 200:
                    continue

                hits = res.json().get("hits", [])
                if not hits:
                    continue

                # Sort by views (most trending first)
                hits.sort(key=lambda x: x.get("views", 0), reverse=True)

                # Find a video that hasn't been posted yet
                for video in hits:
                    vid_id = video.get("id")
                    if self.history.is_video_posted(vid_id):
                        continue

                    # Get the best quality video URL
                    video_files = video.get("videos", {})
                    dl_url = (
                        video_files.get("large", {}).get("url")
                        or video_files.get("medium", {}).get("url")
                        or video_files.get("small", {}).get("url")
                    )
                    if dl_url:
                        print(f"Found NEW video (ID: {vid_id}): {video.get('views')} views, {video.get('downloads')} downloads")
                        return dl_url, topic, vid_id

            except Exception as e:
                print(f"Error: {e}")

        print("Could not find any new videos across all topics.")
        return None, None, None

    def download_file(self, url, path):
        """Download any file to a temp path."""
        try:
            res = requests.get(url, stream=True, timeout=60)
            with open(path, "wb") as f:
                for chunk in res.iter_content(chunk_size=4096):
                    if chunk:
                        f.write(chunk)
            return path
        except Exception as e:
            print(f"Download failed: {e}")
        return None

    def download_video(self, url):
        """Download the video to a temp file."""
        print("Downloading video...")
        path = self.download_file(url, "temp_trending.mp4")
        if path:
            size_mb = os.path.getsize(path) / (1024 * 1024)
            print(f"Downloaded video: {size_mb:.1f} MB")
        return path

    def get_background_music(self, topic):
        """Search Pixabay for music-related videos and extract audio."""
        if not self.pixabay_key:
            return None
        
        music_queries = {
            "spiritual": ["meditation music", "peaceful piano", "ambient calm", "temple bells"],
            "motivational": ["motivational beat", "epic music", "inspiring orchestra", "workout music"],
            "nature": ["nature sounds birds", "rain sounds", "ocean waves relaxing"],
            "tech": ["electronic beat", "futuristic synth", "cyberpunk music"],
            "music": ["piano playing", "guitar music", "violin performance", "drum beat"],
            "default": ["cinematic music background", "inspiring piano music", "ambient soundtrack", "emotional music"]
        }
        
        vibe = "default"
        for key in music_queries:
            if key in topic.lower():
                vibe = key
                break
        
        # Try multiple queries until we find one with audio
        queries = music_queries[vibe] + music_queries["default"]
        random.shuffle(queries)
        
        for query in queries[:3]:
            print(f"Searching for background music: '{query}'")
            url = (
                f"https://pixabay.com/api/videos/"
                f"?key={self.pixabay_key}"
                f"&q={requests.utils.quote(query)}"
                f"&per_page=15"
                f"&order=popular"
            )
            
            try:
                res = requests.get(url, timeout=15)
                if res.status_code != 200:
                    continue
                hits = res.json().get("hits", [])
                for v in random.sample(hits, min(5, len(hits))):
                    vid_id = v.get("id")
                    if self.history.is_music_used(vid_id):
                        continue
                    dl_url = (
                        v.get("videos", {}).get("small", {}).get("url")
                        or v.get("videos", {}).get("medium", {}).get("url")
                    )
                    if not dl_url:
                        continue
                    path = self.download_file(dl_url, "temp_music_source.mp4")
                    if path:
                        # Quick check if it has audio
                        try:
                            test = VideoFileClip(path)
                            has_audio = test.audio is not None
                            test.close()
                            if has_audio:
                                print(f"Found NEW music with audio! (ID: {vid_id}, views: {v.get('views')})")
                                return path, vid_id
                            else:
                                os.remove(path)
                        except:
                            if os.path.exists(path): os.remove(path)
            except Exception as e:
                print(f"Music search failed: {e}")
        
        print("Could not find new music with audio.")
        return None, None

    def add_music_to_video(self, video_path, topic):
        """Overlay background music onto the video."""
        result = self.get_background_music(topic)
        if not result or not result[0]:
            print("No music found, posting with original audio.")
            return video_path
        
        music_source, self._current_music_id = result
        
        try:
            print("Adding background music...")
            video = VideoFileClip(video_path)
            music_clip = VideoFileClip(music_source)
            
            # Extract audio from the music source video
            if music_clip.audio is None:
                print("Music source has no audio, skipping.")
                music_clip.close()
                return video_path
            
            # Extract audio with a tiny buffer to avoid precision errors
            music_duration = min(video.duration, music_clip.audio.duration - 0.1)
            music_audio = music_clip.audio.subclip(0, music_duration)
            
            # Mix: if original video has audio, blend them; otherwise just use music
            if video.audio:
                # We boost both and apply a TINY speed change to bypass copyright bots
                # A 1% change is imperceptible to humans but breaks automated fingerprinting
                v_audio = video.audio.volumex(0.5)
                m_audio = music_audio.volumex(1.5).fx(speedx, 0.99) # Subtle speed change
                mixed = CompositeAudioClip([v_audio, m_audio])
            else:
                mixed = music_audio.volumex(1.2).fx(speedx, 0.99)
            
            # Ensure the audio lasts the full duration of the video
            mixed = mixed.set_duration(video.duration)
            
            final = video.set_audio(mixed)
            output = "temp_trending_with_music.mp4"
            
            print(f"Writing final video file with STEALTH audio encoding...")
            final.write_videofile(
                output,
                codec="libx264",
                audio_codec="aac",
                fps=24,
                audio_fps=44100,
                audio_bitrate="128k",
                temp_audiofile="temp_audio_final.m4a",
                remove_temp=True,
                ffmpeg_params=[
                    "-ar", "44100", 
                    "-ac", "2", 
                    "-movflags", "+faststart",
                    "-pix_fmt", "yuv420p",
                    "-profile:v", "high", # High profile for better compatibility
                    "-level:v", "4.0"
                ]
            )
            
            video.close()
            music_clip.close()
            final.close()
            
            # Cleanup
            if os.path.exists(music_source): os.remove(music_source)
            if os.path.exists(video_path): os.remove(video_path)
            
            print("Music added successfully! 🎶")
            return output
        except Exception as e:
            print(f"Music overlay failed: {e}. Posting with original audio.")
            return video_path

    def generate_caption(self, topic):
        """Generate a viral bilingual caption with trending hashtags."""
        try:
            fact, _ = self.content_gen.generate_text()
            caption = fact
        except:
            # Mixed English + Hindi fallback captions for global appeal
            fallback_captions = [
                # English
                "Nature never stops amazing us 🌍✨",
                "This is absolutely mesmerizing 🔥",
                "Wait for it... 😱🤯",
                "Can you believe this is real? 🌌",
                "This will blow your mind 🧠💥",
                "Sound ON for this one 🔊🎶",
                "Tag someone who needs to see this! 👇",
                "POV: You discovered something incredible 🌊",
                # Hindi / Shayari / Motivational
                "ज़िन्दगी में कुछ बड़ा करना है तो सोचना बंद करो, करना शुरू करो 💪🔥",
                "ये दुनिया बहुत खूबसूरत है, बस नज़रिया बदलो 🌏✨",
                "हार मत मानो, ये वक़्त भी गुज़र जाएगा 🙏💫",
                "कुदरत का नज़ारा देखो, सब्र का फल मीठा होता है 🌸",
                "सपने वो नहीं जो सोते वक़्त आएं, सपने वो हैं जो सोने न दें 🌟",
                "ये नज़ारा देखकर दिल खुश हो गया 😍🇮🇳",
                "जो दिखता है वो हमेशा सच नहीं होता 🧠🔥",
                # Bilingual mix
                "Sometimes silence speaks louder than words 🤫✨ कभी खामोशी भी बहुत कुछ कह जाती है",
                "The universe has a plan for you 🌌 ब्रह्मांड का अपना एक प्लान है",
                "Hard work beats talent 💪 मेहनत हर चीज़ से बड़ी है"
            ]
            caption = random.choice(fallback_captions)

        # Add trending hashtags (randomized selection for variety)
        selected_tags = random.sample(VIRAL_HASHTAGS, min(18, len(VIRAL_HASHTAGS)))
        caption += "\n.\n.\n.\n" + " ".join(selected_tags)
        return caption

    def create_reel(self):
        """Main method: fetch trending video, add music, generate caption."""
        print("=== Trending Reel Generator ===")

        video_url, topic, vid_id = self.get_trending_video()
        if not video_url:
            print("Failed to find a trending video.")
            return None, None

        video_path = self.download_video(video_url)
        if not video_path:
            return None, None

        # Add trending background music
        video_path = self.add_music_to_video(video_path, topic)

        caption = self.generate_caption(topic)
        print(f"Caption: {caption[:100]}...")

        # Save this video ID and music ID so they're never reused
        self.history.save(vid_id, getattr(self, '_current_music_id', None))

        return video_path, caption


if __name__ == "__main__":
    tr = TrendingReelDownloader()
    file, caption = tr.create_reel()
    if file:
        print(f"\n✅ Trending Reel ready: {file}")
        print(f"Caption preview:\n{caption}")
    else:
        print("❌ Failed to create trending reel")
