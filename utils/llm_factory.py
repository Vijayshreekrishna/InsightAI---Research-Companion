import os
import abc
from dotenv import load_dotenv
import google.generativeai as genai
from groq import Groq
from huggingface_hub import InferenceClient

load_dotenv()

class LLMProvider(abc.ABC):
    @abc.abstractmethod
    def generate_content(self, prompt: str) -> str:
        pass

class GeminiProvider(LLMProvider):
    def __init__(self):
        import streamlit as st
        # Priority: Session State -> Environment Variable
        self.api_key = st.session_state.get("user_gemini_key") or os.getenv("GEMINI_API_KEY")
        self.model_name = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found. Please provide it in the sidebar or .env")
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(self.model_name)

    def generate_content(self, prompt: str) -> str:
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Gemini Error: {str(e)}"

class GroqProvider(LLMProvider):
    def __init__(self, model_override=None):
        import streamlit as st
        # Priority: Session State -> Environment Variable
        self.api_key = st.session_state.get("user_groq_key") or os.getenv("GROQ_API_KEY")
        self.model_name = model_override or os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not found. Please provide it in the sidebar or .env")
        self.client = Groq(api_key=self.api_key)

    def generate_content(self, prompt: str) -> str:
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=self.model_name,
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            return f"Groq Error: {str(e)}"

class HuggingFaceProvider(LLMProvider):
    def __init__(self):
        import streamlit as st
        self.token = st.session_state.get("user_hf_key") or os.getenv("HF_TOKEN")
        self.model_name = os.getenv("HF_MODEL", "microsoft/Phi-3-mini-4k-instruct")
        if not self.token:
            raise ValueError("HF_TOKEN not found. Please provide it in the sidebar or .env")
        self.client = InferenceClient(token=self.token)

    def generate_content(self, prompt: str) -> str:
        try:
            messages = [{"role": "user", "content": prompt}]
            response = self.client.chat_completion(
                messages=messages,
                model=self.model_name,
                max_tokens=2000
            ) 
            return response.choices[0].message.content
        except Exception as e:
            return f"Hugging Face Error: {str(e)}"

class OpenAIProvider(LLMProvider):
    def __init__(self):
        import streamlit as st
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError("openai package not installed")
        
        self.api_key = st.session_state.get("user_openai_key") or os.getenv("OPENAI_API_KEY")
        self.model_name = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found. Please provide it in the sidebar or .env")
        self.client = OpenAI(api_key=self.api_key)

    def generate_content(self, prompt: str) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"OpenAI Error: {str(e)}"

def get_llm_provider() -> LLMProvider:
    import streamlit as st
    
    # Use session state if available, otherwise fallback to .env
    provider_name = st.session_state.get("llm_provider", os.getenv("LLM_PROVIDER", "groq")).lower()
    model_name = st.session_state.get("llm_model", None)
    
    if provider_name == "gemini":
        return GeminiProvider()
    elif provider_name == "groq":
        return GroqProvider(model_override=model_name)
    elif provider_name == "huggingface":
        return HuggingFaceProvider()
    elif provider_name == "openai":
        return OpenAIProvider()
    else:
        raise ValueError(f"Unknown LLM_PROVIDER: {provider_name}")
