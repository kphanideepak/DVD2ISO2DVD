# Contributing to DVD ↔ ISO Tool

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [How to Contribute](#how-to-contribute)
- [Development Guidelines](#development-guidelines)
- [Pull Request Process](#pull-request-process)
- [Reporting Bugs](#reporting-bugs)
- [Suggesting Features](#suggesting-features)

## Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](https://www.contributor-covenant.org/version/2/1/code_of_conduct/). By participating, you are expected to uphold this code. Please report unacceptable behavior to the project maintainers.

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- A development environment (VS Code, PyCharm, etc.)
- Access to optical drive hardware for testing (or virtual environment)

### Setting Up Your Development Environment

1. **Fork the repository**
   
   Click the "Fork" button on GitHub to create your own copy.

2. **Clone your fork**
   ```bash
   git clone https://github.com/YOUR_USERNAME/dvd-iso-tool.git
   cd dvd-iso-tool
   ```

3. **Set up upstream remote**
   ```bash
   git remote add upstream https://github.com/ORIGINAL_OWNER/dvd-iso-tool.git
   ```

4. **Create a virtual environment**
   ```bash
   python -m venv venv
   
   # Activate on Linux/macOS
   source venv/bin/activate
   
   # Activate on Windows
   venv\Scripts\activate
   ```

5. **Install development dependencies**
   ```bash
   pip install -r requirements-dev.txt  # if available
   ```

## How to Contribute

### Types of Contributions

- **Bug fixes**: Fix issues reported in the issue tracker
- **Features**: Implement new functionality (discuss first in an issue)
- **Documentation**: Improve README, add docstrings, create guides
- **Testing**: Add unit tests, integration tests, or test on different platforms
- **Code quality**: Refactoring, type hints, linting fixes

### First-Time Contributors

Look for issues labeled `good first issue` or `help wanted`. These are specifically curated for new contributors.

## Development Guidelines

### Code Style

- Follow [PEP 8](https://pep8.org/) style guidelines
- Use meaningful variable and function names
- Maximum line length: 100 characters
- Use type hints where practical

```python
# Good
def convert_dvd_to_iso(source_device: str, output_path: str) -> bool:
    """Convert a DVD to ISO image.
    
    Args:
        source_device: Path to the DVD device (e.g., '/dev/sr0')
        output_path: Destination path for the ISO file
        
    Returns:
        True if conversion succeeded, False otherwise
    """
    pass

# Avoid
def convert(s, o):
    pass
```

### Documentation

- Add docstrings to all public functions and classes
- Use Google-style docstrings
- Update README.md if adding new features
- Add inline comments for complex logic

### Commit Messages

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```
feat(conversion): add support for dual-layer DVDs

fix(ui): resolve progress bar not updating on Windows

docs(readme): add macOS installation instructions
```

### Branch Naming

Use descriptive branch names:

```
feature/burn-iso-to-dvd
fix/windows-drive-detection
docs/troubleshooting-guide
```

## Pull Request Process

1. **Update your fork**
   ```bash
   git fetch upstream
   git checkout main
   git merge upstream/main
   ```

2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**
   - Write clean, documented code
   - Test on your platform
   - Update documentation if needed

4. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat(scope): description of changes"
   ```

5. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Create a Pull Request**
   - Go to GitHub and create a PR from your branch
   - Fill out the PR template completely
   - Link any related issues

7. **Review process**
   - Maintainers will review your PR
   - Address any requested changes
   - Once approved, your PR will be merged

### PR Checklist

Before submitting, ensure:

- [ ] Code follows the project's style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex code
- [ ] Documentation updated (if applicable)
- [ ] No new warnings introduced
- [ ] Tested on at least one platform
- [ ] Commit messages follow conventions

## Reporting Bugs

### Before Submitting

1. Check the [existing issues](https://github.com/yourusername/dvd-iso-tool/issues) to avoid duplicates
2. Try the latest version to see if it's already fixed
3. Collect information about your environment

### Bug Report Template

```markdown
**Describe the bug**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '...'
3. See error

**Expected behavior**
What you expected to happen.

**Screenshots**
If applicable, add screenshots.

**Environment:**
- OS: [e.g., Windows 11, Ubuntu 22.04, macOS 14]
- Python version: [e.g., 3.11.5]
- DVD drive model: [if relevant]

**Additional context**
Any other relevant information.
```

## Suggesting Features

### Feature Request Template

```markdown
**Is your feature request related to a problem?**
A clear description of the problem. Ex. I'm always frustrated when [...]

**Describe the solution you'd like**
A clear description of what you want to happen.

**Describe alternatives you've considered**
Any alternative solutions or features you've considered.

**Additional context**
Any other context, mockups, or screenshots.
```

## Testing

### Running Tests

```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=dvd_iso_tool

# Run specific test file
python -m pytest tests/test_conversion.py
```

### Writing Tests

- Place tests in the `tests/` directory
- Name test files `test_*.py`
- Use descriptive test function names

```python
def test_drive_detection_returns_list():
    """Test that drive detection returns a list of drives."""
    pass

def test_conversion_creates_valid_iso():
    """Test that conversion produces a valid ISO file."""
    pass
```

## Questions?

Feel free to open an issue with the `question` label or start a discussion in GitHub Discussions.

---

Thank you for contributing! 🎉
