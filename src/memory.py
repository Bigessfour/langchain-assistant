from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory

from src.client import create_client, create_llm

# Global memory store
memory_store = {}


def get_session_history(session_id):
    """Get or create memory for a session."""
    if session_id not in memory_store:
        memory_store[session_id] = InMemoryChatMessageHistory()
    return memory_store[session_id]


def clear_session(session_id):
    """Clear memory for a session."""
    if session_id in memory_store:
        del memory_store[session_id]


def build_memory_chatbot():
    """Build a chatbot with conversation memory."""
    client = create_client()
    llm = create_llm(client)

    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant. Remember what the user tells you."),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{input}")
    ])

    chain = prompt | llm

    return RunnableWithMessageHistory(
        chain,
        get_session_history,
        input_messages_key="input",
        history_messages_key="history"
    )


def chat_with_memory(message, session_id="default"):
    """Chat with memory-enabled bot."""
    chatbot = build_memory_chatbot()
    config = {"configurable": {"session_id": session_id}}
    response = chatbot.invoke({"input": message}, config=config)
    return response.content
