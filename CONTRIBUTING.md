# Contributing to CaptchAI

First off, thanks for taking the time to contribute! 🎉

## Table of Contents
- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
  - [Work Coordination](#work-coordination)
  - [Reporting Bugs](#reporting-bugs)
  - [Suggesting Features](#suggesting-features)
  - [Pull Requests](#pull-requests)
- [Development Setup](#development-setup)
- [Style Guidelines](#style-guidelines)

## Code of Conduct

This project follows a Code of Conduct that all contributors are expected to follow. Please read [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) before contributing.

## How Can I Contribute?

### Work Coordination

Before starting any work, please:

1. **Check Existing Issues**: Look through open issues to see if someone is already working on what you plan to do
2. **Create or Comment on Issues**: 
   - If you plan to work on something, create an issue or comment on an existing one
   - Clearly state what you plan to work on and when you expect to start
   - This helps avoid duplicate work and allows for better coordination
3. **Update Issue Status**:
   - Comment on the issue when you start working
   - Keep the issue updated with your progress
   - If you stop working on it, please let others know

This coordination helps everyone work efficiently and avoids wasted effort.

### Reporting Bugs

Before creating bug reports, please check the issue list as you might find out that you don't need to create one. When you are creating a bug report, please include as many details as possible:

* Use a clear and descriptive title
* Describe the exact steps to reproduce the problem
* Provide specific examples to demonstrate the steps
* Describe the behavior you observed after following the steps
* Explain which behavior you expected to see instead and why
* Include any error messages or logs

### Suggesting Features

We welcome feature suggestions! When suggesting a feature:

* Use a clear and descriptive title
* Provide a detailed explanation of how the feature would work
* Explain why this feature would be useful
* List some examples of how it would be used

### Pull Requests

1. Fork the repo and create your branch from `main`
2. If you've added code that should be tested, add tests
3. If you've changed APIs, update the documentation
4. Make sure your code follows our style guidelines
5. Run the test suite
6. Create the pull request!

## Development Setup

1. Clone the repository
```bash
git clone https://github.com/yourusername/captchai.git
cd captchai
```

2. Create a virtual environment and activate it
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -e ".[dev]"
```

4. Set up pre-commit hooks
```bash
pre-commit install
```

## Style Guidelines

We use `ruff` for code formatting and linting. Our code style follows these principles:

- Use type hints for all function parameters and return values
- Follow PEP 8 guidelines
- Use descriptive variable names
- Write docstrings for all public functions and classes
- Keep functions focused and small
- Add comments for complex logic

### Code Formatting

We use `ruff` for code formatting. You can format your code by running:
```bash
ruff format .
```

### Type Checking

We use type hints throughout the codebase. Make sure to add proper type hints to your code.

### Testing

- Write tests for all new features
- Maintain or improve test coverage
- Run the test suite before submitting:
```bash
pytest
```

## License

By contributing to CaptchAI, you agree that your contributions will be licensed under its MIT License. 