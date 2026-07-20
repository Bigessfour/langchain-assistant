from langchain_core.output_parsers import StrOutputParser

from src.client import create_client, create_llm
from src.prompts import get_prompt_by_name


def build_chain(prompt_name="assistant"):
    """Build and return an LCEL chain."""
    prompt = get_prompt_by_name(prompt_name)
    client = create_client()
    llm = create_llm(client)
    return prompt | llm | StrOutputParser()


def chat(language, message):
    """Send a message and get a response."""
    chain = build_chain("assistant")
    return chain.invoke({
        "language": language,
        "message": message,
    })


def summarize(text, length="brief"):
    """Summarize text."""
    chain = build_chain("summarizer")
    return chain.invoke({
        "text": text,
        "length": length,
    })
