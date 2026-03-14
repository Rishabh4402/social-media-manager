import sys
import os
from src.tools.instagram import InstaManager
from src.tools.video import TrendingReelDownloader
from src.tools.llm import ContentGenerator
from src.memory.history import HistoryManager

class InstagramAgent:
    """
    The orchestrator agent that manages the workflow.
    It has access to various tools (Video Tool, LLM Tool, Instagram API Tool)
    and memory management.
    """
    def __init__(self):
        print("Initializing Autonomous Instagram Agent...")
        self.memory = HistoryManager()
        self.llm = ContentGenerator()
        self.video_tool = TrendingReelDownloader()
        self.insta_tool = InstaManager()

    def run(self):
        print("--- Agent Execution Start ---")
        
        max_attempts = 2
        for attempt in range(max_attempts):
            print(f"Attempt {attempt + 1}/{max_attempts}")
            
            # Determine the action path. (We always post reels per current configuration).
            print("Agent Action -> Generating Video Content...")
            video_path, caption = self.video_tool.create_reel()
            
            if not video_path:
                print("Agent Error: Failed to generate content.")
                sys.exit(1)
                
            print(f"Agent Action -> Content ready: {video_path}")

            print("Agent Action -> Logging into Instagram API...")
            if self.insta_tool.login():
                print("Agent Action -> Initiating Post Sequence...")
                media = self.insta_tool.post_reel(video_path, caption)
                
                if media:
                    print(f"Agent Action -> Post created (ID: {media.id}). Starting verification...")
                    
                    # Verify that the audio is actually working on Instagram
                    if self.insta_tool.verify_audio(media.id):
                        print("Agent Action -> Successfully published post with audio!")
                        if os.path.exists(video_path):
                            os.remove(video_path)
                        # Success! Exit loop
                        break
                    else:
                        print("Agent Warning -> Audio check failed! Rolling back post...")
                        self.insta_tool.delete_media(media.id)
                        if attempt < max_attempts - 1:
                            print("Retrying with a different video...")
                            continue
                        else:
                            print("Agent Error: Multiple attempts failed to produce a post with audio.")
                            sys.exit(1)
                else:
                    print("Agent Error: Failed to publish post.")
                    sys.exit(1)
            else:
                print("Agent Error: Instagram login failed.")
                sys.exit(1)

        print("--- Agent Execution Complete ---")
