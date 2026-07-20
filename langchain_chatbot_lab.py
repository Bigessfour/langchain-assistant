"""Lab compatibility wrapper — challenge code lives in src/."""

from src.chains import chat as my_chatbot


def test_chatbot():
    """Run multilingual test cases from the original lab."""
    test_cases = [
        ("English", "Which are better dogs, Chihuahuas or Bulldogs?"),
        ("Spanish", "Explícame qué es la inteligencia artificial"),
        ("French", "Raconte-moi une blague"),
        ("English", "Write a haiku about programming"),
    ]

    print("Testing Multilingual Chatbot")
    print("=" * 40)

    for language, question in test_cases:
        print(f"\nLanguage: {language}")
        print(f"Question: {question}")
        try:
            response = my_chatbot(language, question)
            print(f"Response: {response}")
        except Exception as e:
            print(f"Error: {str(e)}")
        print("-" * 40)


def interactive_mode():
    """Interactive chatbot session."""
    print("Interactive Chatbot Mode")
    print("Type 'quit' to exit")
    print("=" * 30)

    while True:
        language = input(
            "\nEnter language (English/Spanish/French/etc.): "
        ).strip()
        if language.lower() == "quit":
            break

        user_input = input("Your message: ").strip()
        if user_input.lower() == "quit":
            break

        try:
            response = my_chatbot(language, user_input)
            print(f"Bot: {response}")
        except Exception as e:
            print(f"Error: {str(e)}")

    print("Goodbye!")


if __name__ == "__main__":
    interactive_mode()
