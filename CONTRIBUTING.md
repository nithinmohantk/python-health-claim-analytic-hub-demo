# Contributing to HealthClaim Analytics Hub

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to the project.

## Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment for all contributors.

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in [Issues](https://github.com/your-repo/issues)
2. If not, create a new issue with:
   - Clear title and description
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details (OS, Python version, etc.)
   - Relevant error messages or logs

### Suggesting Features

1. Check existing feature requests
2. Create an issue with:
   - Clear description of the feature
   - Use case and benefits
   - Potential implementation approach (if you have ideas)

### Pull Requests

1. **Fork the repository** and create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```
   
   **Branch Naming Conventions:**
   - `feature/description` - New features
   - `bugfix/description` - Bug fixes
   - `hotfix/description` - Critical fixes
   - `docs/description` - Documentation
   - `refactor/description` - Refactoring
   
   See [GitHub Flow Guide](.github/GITHUB_FLOW.md) for details.

2. **Make your changes** following the coding standards below

3. **Write or update tests** for your changes

4. **Run tests and linting**:
   ```bash
   make test
   make lint
   ```

5. **Commit your changes** with clear commit messages:
   ```bash
   git commit -m "Add: feature description"
   ```

6. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Create a Pull Request** with:
   - Clear title following convention (e.g., "Add: feature description")
   - Detailed description using the PR template
   - Reference to related issues (use "Closes #123" or "Fixes #456")
   - Screenshots (for UI changes)
   
   The PR template will automatically populate when creating a PR. See [Branch Protection Rules](.github/BRANCH_PROTECTION.md) for requirements.

## Coding Standards

### Python Style Guide

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Use type hints for function parameters and return types
- Maximum line length: 100 characters
- Use descriptive variable and function names

### Code Formatting

We use `black` for code formatting and `isort` for import sorting:

```bash
make format
```

### Type Checking

We use `mypy` for type checking:

```bash
make type-check
```

### Documentation

- Add docstrings to all functions and classes (Google style)
- Update README.md if adding new features
- Add examples for complex functionality

### Testing

- Write tests for new features
- Aim for >80% code coverage
- Use descriptive test names
- Mock external dependencies (APIs, file I/O)

```bash
# Run tests
make test

# Run with coverage
make test-cov
```

## Project Structure

```
python-streamlit-gpt-dataviz-agent/
├── app.py              # Main Streamlit application
├── utils/              # Core modules
│   ├── data.py        # Data loading and processing
│   ├── network.py     # Network analysis
│   ├── anomaly.py     # Anomaly detection
│   └── gpt.py         # GPT integration
├── tests/             # Test suite
├── docs/              # Documentation
└── .streamlit/        # Streamlit configuration
```

## Development Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-repo/python-streamlit-gpt-dataviz-agent.git
   cd python-streamlit-gpt-dataviz-agent
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   make install-dev
   ```

4. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

5. **Run the application**:
   ```bash
   make run
   ```

## Commit Message Guidelines

Use clear, descriptive commit messages:

- **Add**: New feature
- **Fix**: Bug fix
- **Update**: Update existing feature
- **Refactor**: Code refactoring
- **Docs**: Documentation changes
- **Test**: Test additions/changes
- **Style**: Code style changes (formatting, etc.)

Example:
```
Add: Network visualization with interactive filtering
Fix: Handle missing diagnosis codes in data validation
Update: Improve anomaly detection accuracy
```

## Review Process

1. All PRs require at least one approval
2. All CI checks must pass (tests, linting, formatting)
3. Branch protection rules are enforced automatically
4. Maintainers will review for:
   - Code quality and style
   - Test coverage
   - Documentation completeness
   - Security considerations
   
   See [Branch Protection Rules](.github/BRANCH_PROTECTION.md) for complete requirements.

## Questions?

- Open an issue for questions or discussions
- Check existing documentation in `docs/`
- Review existing code for examples

Thank you for contributing! 🎉
