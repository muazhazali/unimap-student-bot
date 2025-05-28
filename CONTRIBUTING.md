# Contributing to UniMAP Student Bot

We welcome contributions to the UniMAP Student Bot project! This document provides guidelines for contributing to this project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [How to Contribute](#how-to-contribute)
- [Development Setup](#development-setup)
- [Submitting Changes](#submitting-changes)
- [Bug Reports](#bug-reports)
- [Feature Requests](#feature-requests)

## Code of Conduct

This project and everyone participating in it is governed by our commitment to creating a welcoming and inclusive environment. By participating, you agree to:

- Be respectful and inclusive
- Accept constructive criticism gracefully
- Focus on what is best for the community
- Show empathy towards other community members

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally
3. Set up the development environment (see [Development Setup](#development-setup))
4. Create a new branch for your changes
5. Make your changes
6. Test your changes
7. Submit a pull request

## How to Contribute

### Types of Contributions

We welcome several types of contributions:

- **Bug fixes**: Help us fix issues and improve stability
- **Feature enhancements**: Add new functionality to the bot
- **Documentation improvements**: Help make the project more accessible
- **Code optimization**: Improve performance and code quality
- **Testing**: Add or improve test coverage

### Development Guidelines

- Follow Python PEP 8 style guidelines
- Write clear, descriptive commit messages
- Add comments for complex logic
- Ensure your code is well-tested
- Update documentation when necessary

## Development Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/unimap-student-bot.git
   cd unimap-student-bot
   ```

2. **Create and activate virtual environment:**
   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your actual values
   ```

5. **Configure your courses:**
   - Edit `config.py` to add your specific course codes and URLs
   - Use the example format provided

## Submitting Changes

### Pull Request Process

1. **Create a feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes:**
   - Follow the coding standards
   - Add tests if applicable
   - Update documentation as needed

3. **Commit your changes:**
   ```bash
   git add .
   git commit -m "Add: Brief description of your changes"
   ```

4. **Push to your fork:**
   ```bash
   git push origin feature/your-feature-name
   ```

5. **Submit a pull request:**
   - Go to the original repository on GitHub
   - Click "New Pull Request"
   - Provide a clear description of your changes
   - Reference any related issues

### Commit Message Guidelines

Use clear and descriptive commit messages:

- `Add: New feature or functionality`
- `Fix: Bug fixes`
- `Update: Changes to existing functionality`
- `Docs: Documentation updates`
- `Refactor: Code improvements without changing functionality`

## Bug Reports

When reporting bugs, please include:

1. **Clear title and description**
2. **Steps to reproduce the issue**
3. **Expected vs actual behavior**
4. **Environment details:**
   - Python version
   - Operating system
   - Bot version/commit hash
5. **Log files or error messages**
6. **Screenshots if applicable**

### Bug Report Template

```markdown
## Bug Description
Brief description of the bug

## Steps to Reproduce
1. Step one
2. Step two
3. Step three

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Environment
- Python version:
- OS:
- Bot version:

## Additional Context
Any other relevant information
```

## Feature Requests

We welcome feature requests! When submitting one, please:

1. **Check existing issues** to avoid duplicates
2. **Provide clear use case** for the feature
3. **Describe the proposed solution**
4. **Consider implementation complexity**
5. **Be open to discussion** about the feature

### Feature Request Template

```markdown
## Feature Description
Brief description of the feature

## Use Case
Why is this feature needed?

## Proposed Solution
How should this feature work?

## Alternatives Considered
Any alternative solutions you've considered

## Additional Context
Any other relevant information
```

## Questions and Support

If you have questions about contributing:

1. Check the [README.md](README.md) for basic information
2. Look through existing issues and discussions
3. Create a new issue with the "question" label
4. Join our community discussions (if applicable)

## Recognition

Contributors will be recognized in:
- GitHub contributors list
- Release notes for significant contributions
- README acknowledgments (for major contributions)

Thank you for your interest in contributing to the UniMAP Student Bot project! 