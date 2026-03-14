from content_gen import ContentGenerator
from trending_reels import TrendingReelDownloader
from social_manager import InstaManager
import os
import sys
import datetime

def get_next_post_type():
    # Always post reels as requested
    return "reel"

def main():
    print("--- Social Media Manager Agent Start ---")
    
    post_type = get_next_post_type()
    print(f"Today's post type: {post_type}")

    file_path = None
    caption = ""

    if post_type == "reel":
        tr = TrendingReelDownloader()
        file_path, caption = tr.create_reel()
    else:
        gen = ContentGenerator()
        file_path, caption = gen.create_post()
    
    if not file_path:
        print("Failed to generate content.")
        sys.exit(1)
        
    print(f"Content ready: {file_path}")

    # Upload to Instagram
    mgr = InstaManager()
    if mgr.login():
        if post_type == "reel":
            success = mgr.post_reel(file_path, caption)
        else:
            success = mgr.post_photo(file_path, caption)
            
        if success:
            print(f"Successfully posted {post_type} to Instagram!")
            if os.path.exists(file_path):
                os.remove(file_path)
        else:
            print(f"Failed to post {post_type}.")
            sys.exit(1)
    else:
        print("Instagram login failed.")
        sys.exit(1)

    print("--- Process Complete ---")

if __name__ == "__main__":
    main()
