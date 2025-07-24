# Contributing Guide

Thank you for your interest in contributing to Jira Cleanup! This guide will help you get started with development and understand our contribution process.

## Development Setup

### Prerequisites

- Python 3.11 or newer
- [Poetry](https://python-poetry.org/) for dependency management
- Git for version control
- (Optional) [Ollama](https://ollama.ai/) for LLM testing

### Getting Started

1. **Fork and clone the repository**:
   ```bash
   git clone https://github.com/yourusername/jira-cleanup.git
   cd jira-cleanup
   ```

2. **Install dependencies with Poetry**:
   ```bash
   poetry install
   ```

3. **Activate the virtual environment**:
   ```bash
   poetry shell
   ```

4. **Set up your development environment**:
   ```bash
   # Copy the example environment file
   cp .env.example .env
   
   # Edit with your development Jira instance details
   nano .env
   ```

5. **Set up the environment**:
   ```bash
   # Set PYTHONPATH to include src directory
   export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
   ```

6. **Verify the setup**:
   ```bash
   # Run the application in dry-run mode
   python -m jiraclean --help
   ```

## Project Structure

Understanding the project structure will help you navigate the codebase:

```
jira_cleanup/
├── src/jiraclean/           # Main application package
│   ├── domain/              # Core business logic (Clean Architecture)
│   │   ├── entities/        # Business entities (Ticket, User, etc.)
│   │   ├── repositories/    # Data access interfaces
│   │   └── services/        # Domain services
│   ├── infrastructure/      # External system implementations
│   │   ├── repositories/    # Repository implementations
│   │   └── services/        # Service implementations
│   ├── jirautil/           # Jira API integration
│   ├── iterators/          # Ticket selection strategies
│   ├── processors/         # Ticket processing logic
│   ├── llm/                # LLM integration
│   ├── prompts/            # LLM prompt templates
│   └── utils/              # Utility functions
├── docs/                   # Documentation
├── tests/                  # Test suite (to be implemented)
└── migration_tools/        # Migration utilities
```

## Architecture Principles

This project follows Clean Architecture principles:

1. **Dependency Inversion**: Inner layers define interfaces that outer layers implement
2. **Domain-Driven Design**: Rich domain entities with business logic
3. **Separation of Concerns**: Clear boundaries between layers
4. **Testability**: Dependencies can be easily mocked and tested

For detailed architecture information, see [Architecture Overview](architecture.md).

## Development Workflow

### Branch Strategy

We use a feature branch workflow:

1. Create a feature branch from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes and commit them:
   ```bash
   git add .
   git commit -m "feat: add new feature description"
   ```

3. Push your branch and create a pull request:
   ```bash
   git push origin feature/your-feature-name
   ```

### Commit Message Format

We follow conventional commits for automated changelog generation:

- `feat:` - New features
- `fix:` - Bug fixes
- `docs:` - Documentation changes
- `refactor:` - Code refactoring
- `test:` - Adding or updating tests
- `chore:` - Maintenance tasks

Examples:
```bash
git commit -m "feat: add support for custom JQL queries"
git commit -m "fix: handle connection timeout errors gracefully"
git commit -m "docs: update installation instructions"
```

## Code Standards

### Python Style

- Follow PEP 8 style guidelines
- Use type hints for all function parameters and return values
- Maximum line length: 88 characters (Black formatter default)
- Use descriptive variable and function names

### Code Quality Tools

We use several tools to maintain code quality:

```bash
# Format code with Black
black src/

# Sort imports with isort
isort src/

# Type checking with mypy
mypy src/

# Linting with ruff
ruff check src/
```

### Testing

While the test suite is still being developed, please ensure:

1. **Manual testing**: Test your changes manually with dry-run mode
2. **Edge cases**: Consider error conditions and edge cases
3. **Documentation**: Update documentation for new features

Future testing will include:
- Unit tests for domain logic
- Integration tests for external systems
- End-to-end tests for complete workflows

## Making Changes

### Adding New Features

1. **Start with the domain**: Define new entities or services in the domain layer
2. **Create interfaces**: Define repository or service interfaces
3. **Implement infrastructure**: Create concrete implementations
4. **Update CLI**: Add command-line options if needed
5. **Document**: Update relevant documentation

### Modifying Existing Features

1. **Understand the current implementation**: Read the existing code and documentation
2. **Identify impact**: Consider what other parts of the system might be affected
3. **Make incremental changes**: Small, focused changes are easier to review
4. **Test thoroughly**: Ensure existing functionality still works

### Bug Fixes

1. **Reproduce the issue**: Create a minimal test case that demonstrates the bug
2. **Identify the root cause**: Understand why the bug occurs
3. **Fix the issue**: Make the minimal change necessary to fix the bug
4. **Verify the fix**: Ensure the bug is resolved and no new issues are introduced

## Extending the System

### Adding New Ticket Iterators

To add a new way of selecting tickets:

1. Create a new class inheriting from `TicketIterator`
2. Implement the required methods
3. Register the iterator in the appropriate factory or registry

### Adding New Processors

To add a new type of ticket processing:

1. Create a new class inheriting from `TicketProcessor`
2. Implement the processing logic
3. Add configuration options if needed

### Adding New LLM Providers

To support a new LLM provider:

1. Create a new service implementing `LlmService`
2. Add configuration options
3. Update documentation

### UI Development Guidelines

The project uses Rich for beautiful terminal output and Typer for modern CLI interfaces:

#### Rich UI Components (`src/jiraclean/ui/`)

- **Console Singleton**: Use `from jiraclean.ui.console import console` for all output
- **Reusable Components**: Create components in `ui/components.py` for consistent styling
- **Formatters**: Add new formatters in `ui/formatters.py` for different data types
- **Theme Consistency**: Follow the established color scheme and styling patterns

#### Typer CLI Development (`src/jiraclean/cli/`)

- **Command Structure**: Add new commands in `cli/commands.py`
- **Rich Integration**: Use Rich formatting for all command output
- **Help Text**: Include emojis and clear descriptions for better UX
- **Validation**: Use Typer's built-in validation features

#### UI Development Best Practices

1. **Visual Hierarchy**: Original tickets should be prominently displayed
2. **Clear Distinction**: LLM feedback should be visually different from ticket data
3. **Consistent Styling**: Use the established theme and color patterns
4. **Accessibility**: Ensure good contrast and readable formatting
5. **Responsive Design**: Handle different terminal sizes gracefully

## Documentation

### Updating Documentation

- Keep documentation up-to-date with code changes
- Use clear, concise language
- Include examples where helpful
- Update the appropriate documentation category (user, developer, architecture, changes)

### Documentation Structure

- **User docs**: For end users of the tool
- **Developer docs**: For contributors and developers
- **Architecture docs**: For system architects and senior developers
- **Changes docs**: For tracking project evolution

## Pull Request Process

### Before Submitting

1. **Test your changes**: Ensure everything works as expected
2. **Update documentation**: Include relevant documentation updates
3. **Check code quality**: Run formatting and linting tools
4. **Write a clear description**: Explain what your changes do and why

### Pull Request Template

When creating a pull request, include:

1. **Description**: What does this PR do?
2. **Motivation**: Why is this change needed?
3. **Testing**: How was this tested?
4. **Documentation**: What documentation was updated?
5. **Breaking changes**: Are there any breaking changes?

### Review Process

1. **Automated checks**: Ensure all CI checks pass
2. **Code review**: Address feedback from reviewers
3. **Testing**: Verify the changes work as expected
4. **Merge**: Once approved, the PR will be merged

## Getting Help

### Resources

- [Architecture Overview](architecture.md) - Understanding the system design
- [Code Guidelines](code-guidelines.md) - Detailed coding standards
- [User Documentation](../user/) - Understanding how the tool works

### Communication

- **Issues**: Use GitHub issues for bug reports and feature requests
- **Discussions**: Use GitHub discussions for questions and ideas
- **Pull Requests**: Use PR comments for code-specific discussions

### Common Questions

**Q: How do I test my changes without affecting real Jira tickets?**
A: Always use dry-run mode (`--dry-run`) during development. This shows what would happen without making actual changes.

**Q: How do I add a new configuration option?**
A: Add the option to the environment variable handling, update the CLI argument parser, and document it in the configuration guide.

**Q: How do I understand the existing code?**
A: Start with the [Architecture Overview](architecture.md) to understand the high-level design, then explore the domain layer to understand the business logic.

## Code of Conduct

We are committed to providing a welcoming and inclusive environment for all contributors. Please:

- Be respectful and constructive in all interactions
- Focus on the code and ideas, not the person
- Help create a positive learning environment
- Report any unacceptable behavior to the maintainers

## Recognition

Contributors will be recognized in:
- The project's contributor list
- Release notes for significant contributions
- Special recognition for major features or improvements

Thank you for contributing to Jira Cleanup!
