from src.chains import generate_and_evaluate, research_pipeline
from src.memory import chat_with_memory, clear_session
from src.tools import calculator, get_time, word_counter


def test_chains():
    print("=" * 50)
    print("TESTING CHAINS")
    print("=" * 50)

    print("\n--- Simple Chain ---")
    result = generate_and_evaluate("mobile app ideas")
    print(f"Result: {result}")

    print("\n--- Research Pipeline ---")
    result = research_pipeline("renewable energy")
    print(f"Research: {result['research'][:100]}...")
    print(f"Outline: {result['outline'][:100]}...")
    print(f"Summary: {result['summary'][:100]}...")


def test_memory():
    print("\n" + "=" * 50)
    print("TESTING MEMORY")
    print("=" * 50)

    clear_session("demo")

    print("\n--- Conversation ---")
    response1 = chat_with_memory("Hi, my name is Alice", "demo")
    print(f"Bot: {response1}")

    response2 = chat_with_memory("What's my name?", "demo")
    print(f"Bot: {response2}")


def test_tools():
    print("\n" + "=" * 50)
    print("TESTING TOOLS")
    print("=" * 50)

    print(f"\nCalculator: {calculator('25 * 4')}")
    print(f"Time: {get_time('long')}")
    print(f"Words: {word_counter('This is a test sentence')}")


if __name__ == "__main__":
    test_tools()      # Test tools first (no AWS needed)
    test_chains()     # Then chains
    test_memory()     # Then memory
