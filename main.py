from content_gen import ContentGenerator
from social_manager import InstaManager
import os
import sys

def main():
    print("--- Social Media Manager Agent Start ---")
    
    # 1. Generate Content
    gen = ContentGenerator()
    file_path, caption = gen.create_post()
    
    if not file_path:
        print("Failed to generate content.")
        sys.exit(1)
        
    print(f"Content ready: {file_path}")
    print(f"Caption: {caption}")

    # 2. Upload to Instagram
    mgr = InstaManager()
    if mgr.login():
        success = mgr.post_photo(file_path, caption)
        if success:
            print("Successfully posted to Instagram!")
            # Clean up
            if os.path.exists(file_path):
                os.remove(file_path)
        else:
            print("Failed to post to Instagram.")
            sys.exit(1)
    else:
        print("Instagram login failed.")
        sys.exit(1)

    print("--- Process Complete ---")

if __name__ == "__main__":
    main()
