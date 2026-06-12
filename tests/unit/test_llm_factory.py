import pytest
from server.services.llm_factory import LLMFactory, GeminiProvider, GroqProvider, GemmaProvider

def test_llm_factory_gemini():
    provider = LLMFactory.get_provider("gemini")
    assert isinstance(provider, GeminiProvider)

def test_llm_factory_groq():
    provider = LLMFactory.get_provider("groq")
    assert isinstance(provider, GroqProvider)

def test_llm_factory_unknown():
    with pytest.raises(ValueError) as exc:
        LLMFactory.get_provider("unknown_model")
    assert "Unknown LLM provider: unknown_model" in str(exc.value)

def test_gemini_provider_invalid_key():
    provider = GeminiProvider()
    with pytest.raises(ValueError) as exc:
        provider.generate_content("Hello", "bad")
    assert "Invalid Gemini API Key" in str(exc.value)

def test_groq_provider_invalid_key():
    provider = GroqProvider()
    with pytest.raises(ValueError) as exc:
        provider.generate_content("Hello", "bad")
    assert "Invalid Groq API Key" in str(exc.value)

from unittest.mock import patch

def test_llm_factory_gemma():
    provider = LLMFactory.get_provider("gemma", host_url="http://test")
    assert isinstance(provider, GemmaProvider)
    assert provider.host_url == "http://test"

def test_gemma_provider_missing_host():
    provider = GemmaProvider(host_url=None)
    with pytest.raises(ValueError) as exc:
        provider.generate_content("Hello", "key")
    assert "LLM Host URL is not configured" in str(exc.value)

@patch("requests.post")
def test_gemma_provider_success(mock_post):
    provider = GemmaProvider(host_url="http://test")
    mock_response = mock_post.return_value
    mock_response.json.return_value = {"response": "Gemma Answer"}
    mock_response.raise_for_status.return_value = None
    
    res = provider.generate_content("Hello", "key")
    assert res == "Gemma Answer"
    mock_post.assert_called_once()
