import os
import json
from unittest.mock import patch, MagicMock
import pytest

# Set the OPENAI_API_KEY environment variable for testing purposes
os.environ["OPENAI_API_KEY"] = "test_key"

from api.helpers.helper_AI import get_recipe_from_prompt

# Mock response from the OpenAI API
mock_ai_response = {
    "choices": [{
        "message": {"content": json.dumps({
            "title": "Mock Recipe",
            "ingredients": ["Mock Ingredient 1", "Mock Ingredient 2"],
            "steps": ["Mock Step 1", "Mock Step 2"]
        })}
    }]
}

@pytest.fixture(autouse=True)
def mock_openai_response():
    with patch('api.helpers.helper_AI.openai.ChatCompletion.create', MagicMock(return_value=mock_ai_response)) as _mock:
        yield _mock


def test_get_recipe_from_prompt():
    user_input = "admin: mock recipe request"

    # Now the mock applies to where the method is actually imported and used
    response = get_recipe_from_prompt(user_input)
    
    assert "title" in response, "The response dictionary must contain a 'title' key"
    assert "ingredients" in response, "The response dictionary must contain an 'ingredients' key"
    assert "steps" in response, "The response dictionary must contain a 'steps' key"
    assert isinstance(response["title"], str), "'title' should be a string"
    assert isinstance(response["ingredients"], list), "'ingredients' should be a list"
    assert isinstance(response["steps"], list), "'steps' should be a list"
    assert len(response["ingredients"]) > 0, "'ingredients' list should not be empty"
    assert len(response["steps"]) > 0, "'steps' list should not be empty"
