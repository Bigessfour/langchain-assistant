"""Lab compatibility wrapper — challenge code lives in src/."""

from src.memory import chat_with_memory, clear_session


def test_chatbot():
    """Run sample chat turns with memory (Day 2)."""
    clear_session("lab-demo")
    test_cases = [
        "Hi, my name is Alice",
        "What's my name?",
        "Write a haiku about programming",
    ]

    print("Testing Memory Chatbot")
    print("=" * 40)

    for message in test_cases:
        print(f"\nYou: {message}")
        try:
            response = chat_with_memory(message, "lab-demo")
            print(f"Bot: {response}")
        except Exception as e:
            print(f"Error: {str(e)}")
        print("-" * 40)


def interactive_mode():
    """Interactive chatbot session with memory."""
    print("Interactive Memory Chatbot Mode")
    print("Type 'quit' to exit")
    print("=" * 30)

    session_id = "lab-interactive"
    clear_session(session_id)

    while True:
        user_input = input("Your message: ").strip()
        if user_input.lower() == "quit":
            break

        try:
            response = chat_with_memory(user_input, session_id)
            print(f"Bot: {response}")
        except Exception as e:
            print(f"Error: {str(e)}")

    print("Goodbye!")


if __name__ == "__main__":
    interactive_mode()
