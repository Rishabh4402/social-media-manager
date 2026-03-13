from google import genai
import os
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

print("Listing models with details...")
try:
    for m in client.models.list():
        print(f"Name: {m.name}")
        print(f"  Display Name: {m.display_name}")
        print(f"  Description: {m.description}")
        print("-" * 20)
except Exception as e:
    print(f"Failed to list models: {e}")
