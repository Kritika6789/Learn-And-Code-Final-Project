import pytest
from unittest.mock import MagicMock
from server.services.ai_matcher import GenericMatchingStrategy
from server.services.llm_factory import ILLMProvider

def test_generic_matching_strategy_success():
    mock_provider = MagicMock(spec=ILLMProvider)
    mock_provider.generate_content.return_value = "Mocked Match Result"
    
    strategy = GenericMatchingStrategy(mock_provider)
    result = strategy.match_skills("my prompt", "valid_api_key")
    
    assert result == "Mocked Match Result"
    mock_provider.generate_content.assert_called_once_with("my prompt", "valid_api_key")

def test_generic_matching_strategy_invalid_key():
    mock_provider = MagicMock(spec=ILLMProvider)
    strategy = GenericMatchingStrategy(mock_provider)
    
    # Key is None
    result1 = strategy.match_skills("my prompt", None)
    assert "Invalid API Key" in result1
    
    # Key is too short
    result2 = strategy.match_skills("my prompt", "bad")
    assert "Invalid API Key" in result2
    mock_provider.generate_content.assert_not_called()

def test_generic_matching_strategy_exception():
    mock_provider = MagicMock(spec=ILLMProvider)
    mock_provider.generate_content.side_effect = Exception("API Down")
    
    strategy = GenericMatchingStrategy(mock_provider)
    result = strategy.match_skills("my prompt", "valid_api_key")
    
    assert "AI Error: API Down" in result
    mock_provider.generate_content.assert_called_once()
