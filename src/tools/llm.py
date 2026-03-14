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
        self.gemini_key = os.getenv("GEMINI_API_KEY")
        self.hf_token = os.getenv("HF_TOKEN")
        self.niche = os.getenv("CONTENT_NICHE", "Fascinating Space Facts")
        
        if self.gemini_key and not self.gemini_key.startswith("your_"):
            try:
                self.client = genai.Client(api_key=self.gemini_key)
                self.model_id = "gemini-flash-latest"
            except:
                self.client = None
        else:
            self.client = None

    def generate_text_gemini(self, prompt, system_instruction):
        if not self.client:
            return None
        
        # New google-genai SDK config for system instruction
        from google.genai import types
        config = types.GenerateContentConfig(
            system_instruction=system_instruction,
        )
        
        response = self.client.models.generate_content(
            model=self.model_id,
            contents=prompt,
            config=config
        )
        return response.text.strip()

    def generate_text_hf(self, prompt, system_instruction):
        if not self.hf_token:
            return None
        
        # Using Mistral or GPT-2 as a free fallback on Hugging Face
        API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
        headers = {"Authorization": f"Bearer {self.hf_token}"}
        
        # Mistral uses <<SYS>> for system prompt injection
        formatted_prompt = f"<s>[INST] <<SYS>>\n{system_instruction}\n<</SYS>>\n\n{prompt} [/INST]"
        response = requests.post(API_URL, headers=headers, json={"inputs": formatted_prompt})
        
        if response.status_code == 200:
            res_json = response.json()
            if isinstance(res_json, list) and len(res_json) > 0:
                return res_json[0].get('generated_text', '').split('[/INST]')[-1].strip()
        return None

    def generate_text(self):
        # Adding a random "vibe" or "angle" to force variety
        angles = ["mind-blowing", "unbelievable", "odd but true", "terrifyingly cool", "obscure", "viral-style"]
        angle = random.choice(angles)
        
        try:
            # Resolve absolute path from project root
            base_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            prompt_path = os.path.join(base_path, "system_instructions", "instagram_manager.xml")
            with open(prompt_path, "r") as f:
                system_instruction = f.read().strip()
        except Exception as e:
            print(f"Could not read {prompt_path}: {e}")
            system_instruction = (
                "You are an expert social media content creator. Generate a fascinating, unique fact. "
                "Rules: One sentence only. No vulgarity, no sensitive matters. "
                "Format: the fact on the first line, then on a new line provide a 3-word image prompt for a cinematic background."
            )
        
        prompt = (
            f"Topic Niche: {self.niche}\n"
            f"Vibe to use: {angle}\n"
            f"Randomness seed: {random.randint(1, 1000000)}"
        )
        
        text = None
        # Try Gemini First
        try:
            text = self.generate_text_gemini(prompt, system_instruction)
        except Exception as e:
            print(f"Gemini failed: {e}")
        
        # Try Hugging Face Second
        if not text:
            print("Trying fallback / Hugging Face...")
            text = self.generate_text_hf(prompt, system_instruction)
            
        if not text:
            raise Exception("All text generation sources failed. Please check your API keys.")

        # Simple extraction logic
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        fact = lines[0].replace('"', '')
        image_prompt = lines[-1] if len(lines) > 1 else self.niche
        
        return fact, image_prompt

    def generate_image(self, prompt):
        encoded_prompt = requests.utils.quote(prompt)
        p_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1080&height=1350&nologo=true"
        f_url = f"https://loremflickr.com/1080/1350/{prompt.replace(' ', ',')}"
        
        for url in [p_url, f_url]:
            try:
                print(f"Trying image source: {url}")
                response = requests.get(url, timeout=30)
                if response.status_code == 200:
                    if response.content.startswith(b'\xff\xd8') or b"png" in response.content[:100].lower():
                        return Image.open(io.BytesIO(response.content))
            except Exception as e:
                print(f"Source {url} failed: {e}")
        return None

    def overlay_text(self, image, text):
        draw = ImageDraw.Draw(image)
        width, height = image.size
        
        font = None
        try:
            font_paths = [
                "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
                "/System/Library/Fonts/Helvetica.ttc",
                "/Library/Fonts/Arial.ttf"
            ]
            for path in font_paths:
                if os.path.exists(path):
                    font = ImageFont.truetype(path, 60)
                    break
        except:
            pass

        if not font:
            font = ImageFont.load_default()

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

        overlay = Image.new('RGBA', image.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(overlay)
        line_height = 80
        total_height = len(lines) * line_height
        y = (height - total_height) // 2
        d.rectangle([50, y-20, width-50, y+total_height+20], fill=(0, 0, 0, 160))
        image.paste(overlay, (0, 0), overlay)
        
        draw = ImageDraw.Draw(image)
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            x = (width - (bbox[2] - bbox[0])) // 2
            draw.text((x, y), line, font=font, fill="white")
            y += line_height

        return image

    def create_post(self):
        try:
            fact, img_prompt = self.generate_text()
            image = self.generate_image(img_prompt)
            if not image: return None, None
            final_image = self.overlay_text(image, fact)
            filename = "temp_post.jpg"
            final_image.convert('RGB').save(filename)
            return filename, fact
        except Exception as e:
            print(f"Error: {e}")
            return None, None

if __name__ == "__main__":
    gen = ContentGenerator()
    f, c = gen.create_post()
    if f: print(f"Output: {f}")
