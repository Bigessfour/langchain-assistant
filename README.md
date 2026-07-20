# LangChain Assistant

![Test](https://github.com/Bigessfour/langchain-assistant/actions/workflows/test.yml/badge.svg)

Week 13 Day 1 — multilingual AI assistant built with LangChain and AWS Bedrock.

[Challenge brief](https://github.com/codeplatoon-devops/aico-challenges-w13/blob/main/day-1-langchain-foundations/challenge-1-build-your-first-ai-powered-application.md)

## Setup

1. Create virtual environment:

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Configure AWS credentials in `.env`:

   ```text
   AWS_PROFILE=codeplatoon
   AWS_DEFAULT_REGION=us-east-1
   ```

## Run

```bash
# Challenge entry point
python main.py

# Lab wrapper (interactive CLI)
python langchain_chatbot_lab.py

# Streamlit web UI
streamlit run streamlit_app.py
```

## Test

```bash
pytest tests/ -v
flake8 src/ tests/ main.py
```

## Project layout

```text
langchain-assistant/
├── .github/workflows/
│   ├── lint.yml
│   └── test.yml
├── src/
│   ├── client.py
│   ├── prompts.py
│   └── chains.py
├── tests/
│   └── test_prompts.py
├── main.py
├── langchain_chatbot_lab.py
├── streamlit_app.py
├── requirements.txt
└── README.md
```
