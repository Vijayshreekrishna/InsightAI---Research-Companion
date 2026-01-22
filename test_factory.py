import os
from utils.llm_factory import get_llm_provider
from dotenv import load_dotenv

load_dotenv()

def test_provider(provider_name):
    print(f"\n--- Testing Provider: {provider_name} ---")
    os.environ["LLM_PROVIDER"] = provider_name
    
    try:
        provider = get_llm_provider()
        print(f"Successfully initialized {provider.__class__.__name__}")
        
        # We won't actually call generate_content here to avoid errors if keys are missing
        # We just want to ensure the factory works and configuration is read
        if provider_name == "gemini":
            print(f"  API Key Present: {bool(os.getenv('GEMINI_API_KEY'))}")
        elif provider_name == "groq":
            print(f"  API Key Present: {bool(os.getenv('GROQ_API_KEY'))}")
        elif provider_name == "huggingface":
            print(f"  Token Present: {bool(os.getenv('HF_TOKEN'))}")
            
    except Exception as e:
        print(f"Initialization Failed: {e}")

if __name__ == "__main__":
    print("Verifying LLM Factory...")
    test_provider("gemini")
    test_provider("groq")
    test_provider("huggingface")
    test_provider("openai")
