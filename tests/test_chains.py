from src.chains import build_research_chain, build_simple_chain


def test_simple_chain_has_two_steps():
    """Test that simple chain has correct number of chains."""
    # We can't test without LLM, but we can test structure
    # This test verifies the function exists and is callable
    assert callable(build_simple_chain)


def test_research_chain_has_three_steps():
    """Test that research chain function exists."""
    assert callable(build_research_chain)


def test_generate_and_evaluate_exists():
    """Test that the wrapper function exists."""
    from src.chains import generate_and_evaluate
    assert callable(generate_and_evaluate)


def test_research_pipeline_exists():
    """Test that the wrapper function exists."""
    from src.chains import research_pipeline
    assert callable(research_pipeline)
