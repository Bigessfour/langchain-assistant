import pytest

from src.prompts import (
    get_assistant_prompt,
    get_prompt_by_name,
    get_summarizer_prompt,
)


def test_assistant_prompt_formats():
    """Test that assistant prompt formats correctly."""
    prompt = get_assistant_prompt()
    messages = prompt.format_messages(language="Spanish", message="Hello")
    rendered = " ".join(str(message.content) for message in messages)
    assert "Spanish" in rendered
    assert "Hello" in rendered


def test_summarizer_prompt_formats():
    """Test that summarizer prompt formats correctly."""
    prompt = get_summarizer_prompt()
    result = prompt.format(length="brief", text="Some text here")
    assert "brief" in result
    assert "Some text here" in result


def test_get_prompt_by_name_assistant():
    """Test getting assistant prompt by name."""
    prompt = get_prompt_by_name("assistant")
    assert "language" in prompt.input_variables
    assert "message" in prompt.input_variables


def test_get_prompt_by_name_summarizer():
    """Test getting summarizer prompt by name."""
    prompt = get_prompt_by_name("summarizer")
    assert "length" in prompt.input_variables
    assert "text" in prompt.input_variables


def test_get_prompt_by_name_invalid():
    """Test that invalid prompt name raises error."""
    with pytest.raises(ValueError):
        get_prompt_by_name("invalid_prompt")
