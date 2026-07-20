from src.chains import chat, summarize


def main():
    print("Testing Multilingual Assistant")
    print("=" * 40)

    response = chat("English", "What is the capital of France?")
    print(f"English: {response}\n")

    response = chat("Spanish", "What is the capital of France?")
    print(f"Spanish: {response}\n")

    text = (
        "LangChain is a framework for developing applications "
        "powered by language models."
    )
    summary = summarize(text, "brief")
    print(f"Summary: {summary}")


if __name__ == "__main__":
    main()
