from langchain_classic.chains.llm import LLMChain
from langchain_classic.chains.sequential import SimpleSequentialChain, SequentialChain
from langchain_core.prompts import PromptTemplate

from src.client import create_client, create_llm
from src.tools import search_files


def build_simple_chain(llm):
    """Build a two-step idea generation and evaluation chain."""
    # Step 1: Generate ideas
    idea_prompt = PromptTemplate(
        input_variables=["topic"],
        template="Generate 3 creative ideas for: {topic}. List them numbered 1-3."
    )
    idea_chain = LLMChain(llm=llm, prompt=idea_prompt)

    # Step 2: Evaluate ideas
    eval_prompt = PromptTemplate(
        input_variables=["ideas"],
        template="Evaluate these ideas and pick the best one. Explain why:\n\n{ideas}"
    )
    eval_chain = LLMChain(llm=llm, prompt=eval_prompt)

    return SimpleSequentialChain(chains=[idea_chain, eval_chain], verbose=True)


def build_research_chain(llm):
    """Build a three-step research pipeline with named outputs."""
    research_chain = LLMChain(
        llm=llm,
        prompt=PromptTemplate(
            input_variables=["topic"],
            template="Research {topic} and provide 3 key facts."
        ),
        output_key="research"
    )

    outline_chain = LLMChain(
        llm=llm,
        prompt=PromptTemplate(
            input_variables=["topic", "research"],
            template="Create a 3-point outline about {topic} using:\n{research}"
        ),
        output_key="outline"
    )

    summary_chain = LLMChain(
        llm=llm,
        prompt=PromptTemplate(
            input_variables=["topic", "outline"],
            template="Write a 2-paragraph summary about {topic} using:\n{outline}"
        ),
        output_key="summary"
    )

    return SequentialChain(
        chains=[research_chain, outline_chain, summary_chain],
        input_variables=["topic"],
        output_variables=["research", "outline", "summary"],
        verbose=True
    )


def generate_and_evaluate(topic):
    """Run the simple chain on a topic."""
    client = create_client()
    llm = create_llm(client)
    chain = build_simple_chain(llm)
    return chain.run(topic)


def research_pipeline(topic):
    """Run the research pipeline on a topic."""
    client = create_client()
    llm = create_llm(client)
    chain = build_research_chain(llm)
    return chain({"topic": topic})


def build_tool_result_chain(llm):
    """Build a chain whose prompt is filled from a prior tool result."""
    prompt = PromptTemplate(
        input_variables=["pattern", "tool_result"],
        template=(
            "You are summarizing a software project from a real file listing.\n"
            "Search pattern: {pattern}\n\n"
            "Tool output (FileSearch):\n{tool_result}\n\n"
            "Write 3-5 sentences describing the project layout. "
            "Only refer to paths that appear in the tool output. "
            "Do not invent files."
        ),
    )
    return LLMChain(llm=llm, prompt=prompt, verbose=True)


def collect_file_search_context(pattern="*.py"):
    """Run the FileSearch tool only (no LLM). Useful for tests and demos."""
    return search_files(pattern)


def summarize_project_files(pattern="*.py"):
    """Stretch: run FileSearch, then chain an LLM summary over that output.

    Returns:
        dict with pattern, tool_result (from the tool), and summary (from the LLM).
    """
    tool_result = collect_file_search_context(pattern)
    client = create_client()
    llm = create_llm(client)
    chain = build_tool_result_chain(llm)
    result = chain.invoke({"pattern": pattern, "tool_result": tool_result})
    if isinstance(result, dict):
        summary = result.get("text", str(result))
    else:
        summary = str(result)
    return {
        "pattern": pattern,
        "tool_result": tool_result,
        "summary": summary,
    }
