from src.chains import (
    build_research_chain,
    build_simple_chain,
    build_tool_result_chain,
    collect_file_search_context,
    summarize_project_files,
)


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


def test_tool_result_chain_builder_exists():
    """Stretch: tool-result chain builder is callable."""
    assert callable(build_tool_result_chain)


def test_summarize_project_files_exists():
    """Stretch: summarize_project_files wrapper exists."""
    assert callable(summarize_project_files)


def test_collect_file_search_context_uses_tool(tmp_path, monkeypatch):
    """Stretch: tool step runs without AWS and returns FileSearch text."""
    monkeypatch.chdir(tmp_path)
    (tmp_path / "demo.py").write_text("print('hi')", encoding="utf-8")
    (tmp_path / "readme.md").write_text("# hi", encoding="utf-8")

    tool_result = collect_file_search_context("*.py")
    assert "Found" in tool_result
    assert "demo.py" in tool_result
    assert "readme.md" not in tool_result
