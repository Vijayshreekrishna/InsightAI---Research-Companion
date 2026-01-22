import os
from dotenv import load_dotenv
from utils.llm_factory import HuggingFaceProvider

load_dotenv()

def test_hf_generation():
    print("Testing Hugging Face Generation...")
    try:
        provider = HuggingFaceProvider()
        response = provider.generate_content("Hello! Are you working?")
        print("\nSuccess! Response:")
        print(response)
    except Exception as e:
        print(f"\nError: {e}")

if __name__ == "__main__":
    test_hf_generation()
