from social_manager import InstaManager
import urllib.request
import os

print('Initializing InstaManager...')
mgr = InstaManager()
if not mgr.login():
    print('Login failed')
    exit(1)

print('Fetching latest user posts...')
user_id = mgr.cl.user_id
medias = mgr.cl.user_medias(user_id, amount=1)

if not medias:
    print('No posts found!')
else:
    media = medias[0]
    print(f'Latest Post ID: {media.pk}')
    print(f'Media Type: {media.media_type}')
    print(f'Product Type: {media.product_type}')
    print(f'Has Audio: {getattr(media, "has_audio", "Unknown")}')
    
    if media.media_type == 2: # Video/Reel
        # Use url property instead of video_url according to instagrapi Media type
        video_url = str(media.video_url)
        print(f'Video URL: {video_url}')
        
        print('Downloading latest reel to verify audio track...')
        out_path = 'downloaded_reel_check.mp4'
        import ssl
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        with urllib.request.urlopen(video_url, context=ctx) as u, open(out_path, 'wb') as f:
            f.write(u.read())
        
        from moviepy.editor import VideoFileClip
        try:
            v_check = VideoFileClip(out_path)
            print(f'Actual Audio Track Found via moviepy: {v_check.audio is not None}')
            if v_check.audio:
                print(f'Audio duration: {v_check.audio.duration}s')
            v_check.close()
        except Exception as e:
            print('Could not parse downloaded video locally:', e)
        
        if os.path.exists(out_path):
            os.remove(out_path)
