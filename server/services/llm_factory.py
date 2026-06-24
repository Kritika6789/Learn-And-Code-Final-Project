from abc import ABC, abstractmethod
import google.generativeai as genai
import requests

class ILLMProvider(ABC):
    """
    Interface for LLM Providers.
    """
    @abstractmethod
    def generate_content(self, prompt: str, api_key: str) -> str:
        pass

class GeminiProvider(ILLMProvider):
    """
    Concrete provider using Google's Gemini API.
    """
    def generate_content(self, prompt: str, api_key: str) -> str:
        if not api_key or len(api_key) < 5:
            raise ValueError("Invalid Gemini API Key")
            
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.5-flash')
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "quota" in error_msg.lower() or "exhausted" in error_msg.lower():
                raise Exception("API Quota Exceeded (429). Please try again later or check billing.")
            else:
                raise Exception(f"An unexpected error occurred while calling the Gemini API: {error_msg}")

class GroqProvider(ILLMProvider):
    """
    Concrete provider using Groq's REST API.
    """
    def generate_content(self, prompt: str, api_key: str) -> str:
        if not api_key or len(api_key) < 5:
            raise ValueError("Invalid Groq API Key")
            
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "llama3-8b-8192",  # Defaulting to a common Groq model
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.5
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
        except requests.exceptions.RequestException as e:
            raise Exception(f"Error calling Groq API: {str(e)}")

class GemmaProvider(ILLMProvider):
    """
    Concrete provider using a self-hosted Gemma API.
    """
    def __init__(self, host_url: str = None):
        self.host_url = host_url

    def generate_content(self, prompt: str, api_key: str) -> str:
        if not self.host_url:
            raise ValueError("LLM Host URL is not configured. Please set it in the Admin System Configuration.")
            
        headers = {
            "apikey": api_key,
            "Content-Type": "application/json"
        }
        payload = {
            "model": "gemma3:12b-it-q8_0",
            "prompt": prompt,
            "stream": False
        }
        
        try:
            response = requests.post(self.host_url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            # Standard Ollama returns 'response'. OpenAI-compatible returns 'message.content'.
            return data.get("response", data.get("message", {}).get("content", str(data)))
        except requests.exceptions.RequestException as e:
            raise Exception(f"Error calling Self-Hosted Gemma API: {str(e)}")

class LLMFactory:
    """
    Factory for instantiating LLM Providers based on configuration.
    """
    @staticmethod
    def get_provider(provider_name: str, host_url: str = None) -> ILLMProvider:
        provider_name = provider_name.strip().lower()
        if "gemini" in provider_name:
            return GeminiProvider()
        elif "groq" in provider_name:
            return GroqProvider()
        elif "gemma" in provider_name:
            return GemmaProvider(host_url=host_url)
        else:
            raise ValueError(f"Unknown LLM provider: {provider_name}")
