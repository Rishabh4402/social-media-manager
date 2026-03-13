from google import genai
import requests
from PIL import Image, ImageDraw, ImageFont
import os
from dotenv import load_dotenv
import io
import random

load_dotenv()

class ContentGenerator:
    def __init__(self):
        self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        self.niche = os.getenv("CONTENT_NICHE", "Fascinating Space Facts")
        self.model_id = "gemini-flash-latest"

    def generate_text(self):
        prompt = f"Generate a short, viral, and fascinating {self.niche}. It should be one sentence long. No vulgarity, no pillory, no sensitive matters. Provide the fact first, then on a new line provide a 3-word image prompt."
        
        response = self.client.models.generate_content(
            model=self.model_id,
            contents=prompt
        )
        text = response.text.strip()
        
        # Simple extraction logic
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        fact = lines[0].replace('"', '')
        image_prompt = lines[-1] if len(lines) > 1 else self.niche
        
        return fact, image_prompt

    def generate_image(self, prompt):
        # Primary: Pollinations.ai
        encoded_prompt = requests.utils.quote(prompt)
        p_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1080&height=1350&nologo=true"
        
        # Fallback: LoremFlickr (based on niche keywords)
        keywords = prompt.replace(" ", ",")
        f_url = f"https://loremflickr.com/1080/1350/{keywords}"
        
        for url in [p_url, f_url]:
            try:
                print(f"Trying image source: {url}")
                response = requests.get(url, timeout=30)
                if response.status_code == 200:
                    if b"jfif" in response.content[:100].lower() or b"png" in response.content[:100].lower() or b"exif" in response.content[:100].lower() or response.content.startswith(b'\xff\xd8'):
                        return Image.open(io.BytesIO(response.content))
            except Exception as e:
                print(f"Source {url} failed: {e}")
        return None

    def overlay_text(self, image, text):
        draw = ImageDraw.Draw(image)
        width, height = image.size
        
        # Use a default font if custom isn't available
        font = None
        try:
            # Common paths for fonts on macOS
            font_paths = [
                "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
                "/System/Library/Fonts/Helvetica.ttc",
                "/System/Library/Fonts/Arial.ttf",
                "/Library/Fonts/Arial.ttf"
            ]
            for path in font_paths:
                if os.path.exists(path):
                    font = ImageFont.truetype(path, 60)
                    break
        except Exception as e:
            print(f"Font loading error: {e}")

        if not font:
            print("Using default font.")
            font = ImageFont.load_default()

        # Wrap text
        max_width = width - 100
        words = text.split()
        lines = []
        current_line = []
        for word in words:
            current_line.append(word)
            test_line = " ".join(current_line)
            bbox = draw.textbbox((0, 0), test_line, font=font)
            if bbox[2] > max_width:
                lines.append(" ".join(current_line[:-1]))
                current_line = [word]
        lines.append(" ".join(current_line))

        # Draw semi-transparent overlay
        overlay = Image.new('RGBA', image.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(overlay)
        
        line_height = 80
        total_height = len(lines) * line_height
        y = (height - total_height) // 2
        
        # Background box for readability
        d.rectangle([50, y-20, width-50, y+total_height+20], fill=(0, 0, 0, 160))
        
        image.paste(overlay, (0, 0), overlay)
        
        # Draw text
        draw = ImageDraw.Draw(image)
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            line_width = bbox[2] - bbox[0]
            x = (width - line_width) // 2
            draw.text((x, y), line, font=font, fill="white")
            y += line_height

        return image

    def create_post(self):
        print("Generating text via Gemini...")
        try:
            fact, img_prompt = self.generate_text()
            print(f"Fact: {fact}")
            print(f"Image Prompt: {img_prompt}")
        except Exception as e:
            print(f"Text generation failed: {e}")
            return None, None
        
        print("Generating image via Pollinations...")
        image = self.generate_image(img_prompt)
        if not image:
            print("Failed to get image.")
            return None, None
            
        print("Applying text overlay...")
        final_image = self.overlay_text(image, fact)
        
        filename = "temp_post.jpg"
        final_image.convert('RGB').save(filename)
        return filename, fact

if __name__ == "__main__":
    gen = ContentGenerator()
    file, caption = gen.create_post()
    if file:
        print(f"Created: {file}")
        print(f"Caption: {caption}")
