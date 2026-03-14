import os
import json

class HistoryManager:
    def __init__(self):
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.history_file = os.path.join(base_path, "posted_history.json")
        self.history = self._load()

    def _load(self):
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, "r") as f:
                    return json.load(f)
            except:
                pass
        return {"posted_ids": [], "used_music_ids": []}

    def save(self, video_id, music_id=None):
        self.history["posted_ids"].append(video_id)
        if music_id:
            self.history.setdefault("used_music_ids", []).append(music_id)
        
        # Keep last 200 entries to avoid infinite growth
        self.history["posted_ids"] = self.history["posted_ids"][-200:]
        self.history["used_music_ids"] = self.history.get("used_music_ids", [])[-200:]
        
        with open(self.history_file, "w") as f:
            json.dump(self.history, f)

    def is_video_posted(self, video_id):
        return video_id in self.history.get("posted_ids", [])

    def is_music_used(self, music_id):
        return music_id in self.history.get("used_music_ids", [])
