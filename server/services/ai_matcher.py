from abc import ABC, abstractmethod
from server.services.llm_factory import ILLMProvider

class IAIMatcher(ABC):
    """
    Strategy interface for AI skill matching (Strategy Pattern - Open/Closed Principle).
    """
    @abstractmethod
    def match_skills(self, prompt: str, api_key: str) -> str:
        pass

class GenericMatchingStrategy(IAIMatcher):
    """
    Concrete strategy using an injected ILLMProvider.
    """
    def __init__(self, provider: ILLMProvider):
        self.provider = provider

    def match_skills(self, prompt: str, api_key: str) -> str:
        if not api_key or len(api_key) < 5:
            return "AI Error: Invalid API Key\n\n(Mocked Results: Priya Sharma is a good match.)"
            
        try:
            return self.provider.generate_content(prompt, api_key)
        except Exception as e:
            error_msg = str(e)
            return f"AI Error: {error_msg}\n\n(Mocked Results: Priya Sharma is a good match.)"
