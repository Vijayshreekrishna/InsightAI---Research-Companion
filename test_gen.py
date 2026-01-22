import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
model_name = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

if not api_key:
    print("Error: GEMINI_API_KEY not found in environment.")
    exit(1)

genai.configure(api_key=api_key)

print(f"Testing generation with configured model: {model_name}...")

try:
    model = genai.GenerativeModel(model_name)
    response = model.generate_content("Hello, this is a test.")
    print("Success! Response received:")
    print(response.text)
except Exception as e:
    print(f"Generation failed: {e}")
