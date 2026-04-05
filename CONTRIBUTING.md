# Contributing to RTorrent MCP Server

Thank you for your interest in contributing to RTorrent MCP Server! This document provides guidelines and information for contributors.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Development Workflow](#development-workflow)
- [Code Style](#code-style)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)
- [Reporting Issues](#reporting-issues)
- [Documentation](#documentation)

## Code of Conduct

This project follows a [Code of Conduct](CODE_OF_CONDUCT.md) to ensure a welcoming environment for all contributors. By participating, you agree to uphold this code.

## Branch Protection Rules

This repository uses GitHub branch protection to maintain code quality:

### Protected Branches

#### `main` Branch
- **Required status checks**: All CI checks must pass
  - `ci-cd` workflow (test, lint, build, release)
  - `codeql` security scanning
- **Required reviews**: At least 1 approval required
- **Include administrators**: Branch protection applies to admins
- **Restrict pushes**: Only maintainers can push directly
- **Allow force pushes**: Disabled
- **Allow deletions**: Disabled

#### `develop` Branch (if used)
- **Required status checks**: Unit tests must pass
- **Required reviews**: At least 1 approval required
- **Include administrators**: Branch protection applies to admins

### Development Workflow

1. **Create feature branches** from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Push your branch** and create a Pull Request:
   - All CI checks must pass
   - At least 1 reviewer approval required
   - Squash merge to keep history clean

3. **Rebase frequently** to stay up-to-date:
   ```bash
   git fetch origin
   git rebase origin/main
   ```

### Branch Naming Convention

- `feature/feature-name`: New features
- `bugfix/bug-description`: Bug fixes
- `hotfix/critical-fix`: Critical production fixes
- `docs/documentation-update`: Documentation changes
- `refactor/code-improvement`: Code refactoring

## Getting Started

### Prerequisites

- Python 3.9 or higher
- Node.js 18+ (for MCPB CLI)
- rTorrent (for testing)
- Git

### Quick Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/rtorrent-mcp.git
cd rtorrent-mcp

# Set up Python environment
python -m venv venv
venv\Scripts\activate  # On Windows
pip install -r requirements.txt
pip install -r requirements.txt[dev]

# Install MCPB CLI
npm install -g @anthropic-ai/mcpb

# Run tests
pytest
```

## Development Setup

### Environment Configuration

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Configure your environment variables:
   ```env
   RTORRENT_HOST=localhost
   RTORRENT_PORT=5000
   LOG_LEVEL=DEBUG
   ```

### IDE Setup

We recommend using:
- **VS Code** with Python extension
- **PyCharm Professional** with MCP support
- **Cursor** for AI-assisted development

## Development Workflow

### 1. Choose an Issue

- Check the [Issues](https://github.com/yourusername/rtorrent-mcp/issues) page
- Look for issues labeled `good first issue` or `help wanted`
- Comment on the issue to indicate you're working on it

### 2. Create a Branch

```bash
# Create and switch to a feature branch
git checkout -b feature/your-feature-name

# Or for bug fixes
git checkout -b fix/issue-number-description
```

### 3. Make Changes

- Write clean, well-documented code
- Add tests for new functionality
- Update documentation as needed
- Follow the code style guidelines

### 4. Test Your Changes

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/rtorrent_mcp --cov-report=html

# Run linting
black --check .
isort --check-only .
mypy src/
```

### 5. Commit Your Changes

```bash
# Stage your changes
git add .

# Commit with a descriptive message
git commit -m "feat: add new torrent search functionality

- Add NYAA.si API integration
- Implement quality scoring algorithm
- Add comprehensive test coverage

Closes #123"
```

### 6. Push and Create PR

```bash
# Push your branch
git push origin feature/your-feature-name

# Create a Pull Request on GitHub
```

## Code Style

### Python Style

We follow [PEP 8](https://pep8.org/) with these tools:

- **Black**: Code formatting (line length: 88)
- **isort**: Import sorting
- **mypy**: Type checking
- **flake8**: Linting

### Commit Messages

We follow [Conventional Commits](https://conventionalcommits.org/):

```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat`: New features
- `fix`: Bug fixes
- `docs`: Documentation
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Testing
- `chore`: Maintenance

### Naming Conventions

- **Variables**: `snake_case`
- **Functions**: `snake_case`
- **Classes**: `PascalCase`
- **Constants**: `UPPER_SNAKE_CASE`
- **Files**: `snake_case.py`

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/unit/test_rtorrent_client.py

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=src/rtorrent_mcp --cov-report=html
```

### Writing Tests

```python
import pytest
from src.rtorrent_mcp.services.rtorrent_client import RTorrentClient

class TestRTorrentClient:
    def test_connection_success(self, mock_server):
        """Test successful connection to rTorrent"""
        client = RTorrentClient()
        result = await client.connect()
        assert result is True
        assert client.connected is True
```

### Test Coverage

- Aim for >90% code coverage
- Include unit tests for all functions
- Add integration tests for API interactions
- Test error conditions and edge cases

## Submitting Changes

### Pull Request Process

1. **Title**: Use descriptive, imperative titles
   - [OK] "Add torrent pause functionality"
   - [FAIL] "Fix bug" or "Update code"

2. **Description**: Include context and details
   - What problem does this solve?
   - How was it implemented?
   - What tests were added?

3. **Checklist**: Ensure all items are checked
   - [ ] Code follows style guidelines
   - [ ] Tests pass locally
   - [ ] Documentation updated
   - [ ] Ready for review

### Review Process

- At least one maintainer must approve
- CI/CD pipeline must pass
- No merge conflicts
- Follow-up commits may be requested

## Reporting Issues

### Bug Reports

Use the [Bug Report template](.github/ISSUE_TEMPLATE/bug-report.yml) and include:

- Clear description of the issue
- Steps to reproduce
- Expected vs. actual behavior
- Environment details
- Error messages/logs

### Feature Requests

Use the [Feature Request template](.github/ISSUE_TEMPLATE/feature-request.yml) and include:

- Clear description of the feature
- Use case and problem it solves
- Proposed implementation
- Alternative solutions considered

## Documentation

### Code Documentation

```python
def search_anime(query: str, resolution: str = "720p") -> List[Dict[str, Any]]:
    """
    Search nyaa.si for anime releases.

    Args:
        query: Anime name to search for
        resolution: Preferred resolution (720p, 1080p, 4K)

    Returns:
        List of anime releases with quality scoring

    Raises:
        ConnectionError: If nyaa.si is unreachable
        ValueError: If query is empty
    """
```

### README Updates

- Update installation instructions
- Add new features to feature list
- Update API examples
- Include breaking changes

## Development Best Practices

### Security

- Never commit sensitive data
- Use environment variables for secrets
- Validate all inputs
- Follow principle of least privilege

### Performance

- Profile code for bottlenecks
- Use async/await for I/O operations
- Cache expensive operations
- Monitor memory usage

### Maintainability

- Write self-documenting code
- Add comprehensive error handling
- Use type hints
- Keep functions small and focused

## Getting Help

- **Documentation**: Check [README.md](README.md) and [PRD](docs/PRD.md)
- **Issues**: Search existing issues or create new ones
- **Discussions**: Use GitHub Discussions for questions
- **Discord**: Join our community Discord (link in README)

## License

By contributing to this project, you agree that your contributions will be licensed under the same license as the project (MIT License).

## Recognition

Contributors are recognized in:
- [CONTRIBUTORS.md](CONTRIBUTORS.md) file
- Release notes
- GitHub's contributor insights

Thank you for contributing to RTorrent MCP Server! 

---

**Last Updated**: September 23, 2025
