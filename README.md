# Jira Cleanup

A configurable, policy-based tool for automated Jira ticket governance and lifecycle management.

## Overview

Jira Cleanup provides a robust framework for implementing governance policies across your Jira projects. It helps maintain clean and efficient Jira workspaces by identifying and addressing tickets that need attention, providing accountability, and closing tickets that are no longer relevant.

### Key Features

- **Automated Governance**: Apply customizable policies across configurable sets of Jira tickets
- **Multi-Provider AI Assessment**: Support for Ollama, OpenAI, Anthropic, and Google LLM providers
- **Multi-Instance Jira Support**: Manage multiple Jira instances with easy switching
- **Safe Testing**: Comprehensive dry-run mode for risk-free testing
- **Flexible Configuration**: Environment variables, command-line options, and template customization
- **Extensible Architecture**: Plugin-ready design for custom iterators, processors, and LLM providers

## Quick Start

```bash
# Install with pipx (recommended)
pipx install git+https://github.com/vacobuilt/jira-cleanup.git

# Or install for development
git clone https://github.com/vacobuilt/jira-cleanup.git
cd jira-cleanup
poetry install

# Configure your environment
cp .env.example .env
# Edit .env with your Jira credentials

# 🎯 Modern CLI with beautiful Rich output
jiraclean main-command --project YOUR_PROJECT --dry-run --max-tickets 5

# 🚀 Interactive setup wizard
jiraclean setup

# ⚙️ Manage configurations
jiraclean config list
jiraclean config show

# 📋 Get help with beautiful formatting
jiraclean --help
jiraclean main-command --help

# For development setup
source venv/bin/activate  # or: poetry shell
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
python -m jiraclean.cli.main main-command --project YOUR_PROJECT --dry-run
```

### ✨ New Features

- **🎨 Beautiful Rich Output**: Tickets displayed in prominent panels with color-coded status
- **🎯 Modern CLI**: Typer-based interface with intuitive commands and auto-completion
- **🔍 Visual Distinction**: Original tickets prominently highlighted, LLM feedback clearly differentiated
- **🚀 Interactive Setup**: Guided configuration wizard for easy onboarding
- **⚙️ Configuration Management**: Multiple Jira instances, easy switching and testing

## Documentation

Our documentation is organized by audience:

### 📖 [User Documentation](docs/user/)
- **[Project Overview](docs/user/README.md)** - Detailed project description and features
- **[Installation Guide](docs/user/installation.md)** - Complete installation instructions
- **[Quick Start Guide](docs/user/quickstart.md)** - Get up and running in minutes
- **[Configuration Guide](docs/user/configuration.md)** - Environment setup and customization

### 👩‍💻 [Developer Documentation](docs/developer/)
- **[Contributing Guide](docs/developer/contributing.md)** - How to contribute to the project
- **[Architecture Overview](docs/developer/architecture.md)** - System design and architecture
- **[Code Guidelines](docs/developer/code-guidelines.md)** - Coding standards and best practices
- **[API Reference](docs/developer/api-reference.md)** - Technical API documentation

### 🏗️ [Architecture Documentation](docs/architecture/)
- **[System Overview](docs/architecture/overview.md)** - Comprehensive architecture analysis

### 📋 [Change Documentation](docs/changes/)
- **[Changelog](docs/changes/changelog.md)** - Version history and release notes
- **[Design Decisions](docs/changes/design-decisions.md)** - Important architectural decisions
- **[Roadmap](docs/changes/roadmap.md)** - Future development plans

## Requirements

- Python 3.11+
- Jira API access (API token recommended)
- Optional: [Ollama](https://ollama.ai/) for LLM-powered assessment

## License

MIT License - see [LICENSE](LICENSE) for details.

## Support

- 📚 **Documentation**: Start with our [User Guide](docs/user/README.md)
- 🐛 **Issues**: Report bugs via [GitHub Issues](https://github.com/vacobuilt/jira-cleanup/issues)
- 💬 **Discussions**: Join conversations in [GitHub Discussions](https://github.com/vacobuilt/jira-cleanup/discussions)
- 🤝 **Contributing**: See our [Contributing Guide](docs/developer/contributing.md)

---

**Ready to get started?** Check out our [Quick Start Guide](docs/user/quickstart.md) or dive into the [full documentation](docs/).
