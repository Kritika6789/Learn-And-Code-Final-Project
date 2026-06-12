import pytest
from server.services.llm_factory import GeminiProvider, GroqProvider

def test_gemini_integration_handles_invalid_key_gracefully():
    provider = GeminiProvider()
    # Ensure it throws an exception or handles REST correctly with a fake key that is at least 5 chars
    with pytest.raises(Exception) as exc:
        provider.generate_content("Say hi", "dummy_key_that_is_long_enough")
    # It should hit the network and fail with a Gemini specific API error
    assert "An unexpected error occurred while calling the Gemini API" in str(exc.value)

def test_groq_integration_handles_invalid_key_gracefully():
    provider = GroqProvider()
    # Ensure it hits the network and gets a 401 Unauthorized from the actual Groq API
    with pytest.raises(Exception) as exc:
        provider.generate_content("Say hi", "dummy_key_that_is_long_enough")
    assert "Error calling Groq API" in str(exc.value)
    assert "401 Client Error: Unauthorized" in str(exc.value)
