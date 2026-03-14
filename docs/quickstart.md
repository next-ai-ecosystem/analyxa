# Quickstart Guide

## Installation

```bash
pip install analyxa
```

## 1. Set Up API Keys

Create a `.env` file in your project root:

```bash
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

Optional (for semantic embeddings):
```bash
OPENAI_API_KEY=sk-your-key-here
```

## 2. Analyze Your First Conversation

### From Python

```python
from analyxa import analyze

conversation = """
User: I can't log into my account. I've tried resetting my password three times.
Agent: I'm sorry you're having trouble. Let me check your account status.
User: This is really frustrating. I have a meeting in 10 minutes and I need access.
Agent: I can see the issue — your account was temporarily locked after multiple failed attempts. I've unlocked it now. Please try logging in again.
User: That worked. Thank you, but the lock policy should be less aggressive.
"""

result = analyze(conversation, schema="support")

# Access extracted fields
print(f"Sentiment: {result.fields['sentiment']}")
print(f"Issue: {result.fields['issue_category']}")
print(f"Resolved: {result.fields['session_outcome']}")
print(f"Effort: {result.fields['customer_effort_score']}")
```

### From CLI

Save the conversation to a file, then:

```bash
analyxa analyze conversation.txt --schema support
```

## 3. Explore Schemas

```bash
# List all available schemas
analyxa schemas list

# See fields in a specific schema
analyxa schemas show support
```

## 4. Batch Processing

```bash
# Analyze all .txt files in a directory
analyxa batch ./conversations/ --schema universal --output-dir ./results/
```

## 5. Production Pipeline (Optional)

Start Redis and Qdrant:

```bash
cd docker && docker compose up -d
```

Push and process conversations:

```bash
analyxa redis push conversation.txt --schema support
analyxa redis process
analyxa search "customer complaint" --limit 5
```

## Next Steps

- [Schema Reference](schemas.md) — All fields and how to create custom schemas
- [API Reference](api-reference.md) — Python API documentation
