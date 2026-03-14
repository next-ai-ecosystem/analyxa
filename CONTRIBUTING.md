# Contributing to Analyxa

Thank you for your interest in contributing to Analyxa!

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/analyxa.git`
3. Set up the development environment:

```bash
cd analyxa
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

4. Run tests to verify your setup:

```bash
python3 -m pytest tests/ -v
```

## Development Workflow

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Make your changes
3. Add tests for new functionality
4. Run all tests: `python3 -m pytest tests/ -v`
5. Commit with a descriptive message: `git commit -m "feat: description"`
6. Push and create a Pull Request

## Creating Custom Schemas

One of the best ways to contribute is creating new vertical schemas:

1. Create a YAML file in `src/analyxa/schemas/`
2. Inherit from `universal` to get the 10 base fields
3. Add your domain-specific fields with clear `prompt_hint` instructions
4. Add example conversations in `examples/conversations/`
5. Add tests in `tests/`

## Code Style

- Python 3.10+ type hints
- Docstrings for public functions
- Tests for all new functionality
- YAML for schemas, not hardcoded fields

## Reporting Issues

Please include:
- Python version
- Analyxa version (`analyxa version`)
- Steps to reproduce
- Expected vs actual behavior

## License

By contributing, you agree that your contributions will be licensed under Apache 2.0.
