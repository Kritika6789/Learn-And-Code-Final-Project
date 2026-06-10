from abc import ABC, abstractmethod
import google.generativeai as genai

class IAIMatcher(ABC):
    """
    Strategy interface for AI skill matching (Strategy Pattern - Open/Closed Principle).
    """
    @abstractmethod
    def match_skills(self, prompt: str, api_key: str) -> str:
        pass

    @abstractmethod
    def generate_risk_summary(self, prompt: str, api_key: str) -> str:
        pass

class GeminiMatchingStrategy(IAIMatcher):
    """
    Concrete strategy using Google's Gemini API.
    """
    def match_skills(self, prompt: str, api_key: str) -> str:
        if not api_key or len(api_key) < 5:
            return "AI Error: Invalid API Key\n\n(Mocked Results: Priya Sharma is a good match.)"
            
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.5-flash')
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "quota" in error_msg.lower() or "exhausted" in error_msg.lower():
                clean_err = "API Quota Exceeded (429). Please try again later or check billing."
            elif "API_KEY_INVALID" in error_msg or "API key not valid" in error_msg:
                clean_err = "Invalid API Key provided. Please update it in the Admin settings."
            else:
                clean_err = "An unexpected error occurred while calling the Gemini API."
            return f"AI Error: {clean_err}\n\n(Mocked Results: Priya Sharma is a good match.)"

    def generate_risk_summary(self, prompt: str, api_key: str) -> str:
        if not api_key or len(api_key) < 5:
            return "AI Error: Invalid API Key\n\nMock: The project looks on track but verify milestone deadlines."
            
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.5-flash')
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "quota" in error_msg.lower() or "exhausted" in error_msg.lower():
                clean_err = "API Quota Exceeded (429)."
            elif "API_KEY_INVALID" in error_msg or "API key not valid" in error_msg:
                clean_err = "Invalid API Key. Please update it in Admin settings."
            else:
                import traceback
                traceback.print_exc()
                clean_err = f"An unexpected error occurred: {error_msg}"
            return f"AI Error: {clean_err}\n\nMock: The project looks on track but verify milestone deadlines."
