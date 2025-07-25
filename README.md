# Jira Cleanup

A configurable, extensible tool for automated Jira ticket analysis and governance with AI-powered insights.

## Overview

Jira Cleanup provides a robust framework for implementing analysis policies across your Jira projects. It helps maintain clean and efficient Jira workspaces by identifying tickets that need attention using multiple analysis types, providing intelligent recommendations, and supporting various LLM providers for AI-powered assessment.

### Key Features

- **🔍 Multiple Analysis Types**: Choose from quiescence analysis, ticket quality assessment, and more
- **🤖 Multi-Provider LLM Support**: Works with Anthropic Claude, OpenAI, Google, and Ollama
- **🎨 Beautiful Rich Output**: Tickets displayed in color-coded panels with domain-specific formatting
- **🛡️ Safe Testing**: Comprehensive dry-run mode for risk-free testing
- **⚙️ Flexible Configuration**: Multiple Jira instances, environment variables, and template customization
- **🏗️ Extensible Architecture**: Plugin-ready design for custom analyzers, result types, and formatters

## Quick Start

### Installation

```bash
# Install with pipx (recommended)
pipx install git+https://github.com/vacobuilt/jira-cleanup.git

# Or install for development
git clone https://github.com/vacobuilt/jira-cleanup.git
cd jira-cleanup
poetry install
```

### Basic Usage

```bash
# 🚀 Interactive setup wizard
jiraclean setup

# ⚙️ Manage Jira instance configurations
jiraclean config list
jiraclean config add

# 🔍 Analyze tickets with quiescence detection
jiraclean --instance personal --project MYPROJ --analyzer quiescent --dry-run

# 🎯 Analyze tickets for quality issues
jiraclean --instance personal --project MYPROJ --analyzer ticket_quality --dry-run

# 🤖 Use different LLM providers
jiraclean --instance personal --project MYPROJ --llm-provider anthropic --llm-model claude-sonnet-4-20250514 --analyzer quiescent --dry-run

jiraclean --instance personal --project MYPROJ --llm-provider openai --llm-model gpt-4 --analyzer ticket_quality --dry-run

# 📊 Process more tickets
jiraclean --instance personal --project MYPROJ --max-tickets 100 --analyzer quiescent --dry-run

# 🎮 Interactive mode with prompts
jiraclean --interactive

# 📋 Get help with beautiful formatting
jiraclean --help
```

### Configuration

```bash
# Set up environment file
cp .env.example .env
# Edit .env with your configuration

# Or use the interactive setup
jiraclean setup --install-templates
```

## Analysis Types

### 🟡 Quiescence Analysis
Identifies stale or inactive tickets that may need attention:
- **Staleness scoring** (1-10 scale)
- **Inactivity day tracking**
- **🟡 QUIESCENT vs 🟢 ACTIVE** status indicators
- **Yellow/blue color scheme** for easy identification

```bash
jiraclean --instance personal --project MYPROJ --analyzer quiescent --dry-run
```

### 🔴 Ticket Quality Analysis
Evaluates ticket quality and suggests improvements:
- **Quality scoring** (1-10 scale)
- **Specific improvement suggestions**
- **🔴 NEEDS IMPROVEMENT vs 🟢 GOOD QUALITY** status indicators
- **Red/green color scheme** for quality assessment

```bash
jiraclean --instance personal --project MYPROJ --analyzer ticket_quality --dry-run
```

## LLM Provider Support

### Supported Providers

| Provider | Models | Configuration |
|----------|--------|---------------|
| **Anthropic** | Claude Sonnet 4, Claude Haiku | API key required |
| **OpenAI** | GPT-4, GPT-3.5-turbo | API key required |
| **Google** | Gemini Pro, Gemini Flash | API key required |
| **Ollama** | Llama 3.2, Mistral, etc. | Local installation |

### Provider Examples

```bash
# Anthropic Claude
jiraclean --llm-provider anthropic --llm-model claude-sonnet-4-20250514 --analyzer quiescent

# OpenAI GPT-4
jiraclean --llm-provider openai --llm-model gpt-4 --analyzer ticket_quality

# Google Gemini
jiraclean --llm-provider google --llm-model gemini-pro --analyzer quiescent

# Local Ollama
jiraclean --llm-provider ollama --llm-model llama3.2:latest --ollama-url http://localhost:11434
```

## Command Reference

### Main Options

```
🎫 Jira Cleanup - A configurable tool for Jira ticket governance

Options:
  -p, --project TEXT              🎯 Jira project key to process
  --dry-run / --production        🔍 Run in dry-run mode (safe) or production mode
  -n, --max-tickets INTEGER       📊 Maximum number of tickets to process [1-1000]
  --debug                         🐛 Enable debug logging
  --llm-provider TEXT             🤖 LLM provider (ollama, openai, anthropic, google)
  -m, --llm-model TEXT            🤖 LLM model to use for assessment
  --analyzer TEXT                 🔍 Analyzer type (quiescent, ticket_quality)
  --ollama-url TEXT               🔗 URL for Ollama API
  --with-llm / --no-llm           🧠 Enable or disable LLM assessment
  -e, --env-file PATH             📄 Path to .env file with configuration
  -i, --instance TEXT             🏢 Jira instance to use
  --interactive                   🎮 Interactive mode with prompts
  -h, --help                      Show help message

Commands:
  config   ⚙️ Manage Jira instance configurations
  setup    🚀 Set up Jira Cleanup configuration and templates
```

### Configuration Commands

```bash
# List configured Jira instances
jiraclean config list

# Add a new Jira instance
jiraclean config add

# Show configuration details
jiraclean config show

# Set up templates and configuration
jiraclean setup --install-templates
```

## Architecture

### Extensible Analysis Framework

Jira Cleanup uses a **triple pattern architecture** that makes it easy to add new analysis types:

```
Analyzer → Result → Formatter
```

**Current Implementations:**
- `QuiescentAnalyzer` → `QuiescentResult` → `QuiescentFormatter`
- `TicketQualityAnalyzer` → `QualityResult` → `QualityFormatter`

**Adding New Analyzers:**
1. Create your analyzer class implementing `BaseTicketAnalyzer`
2. Define your result type extending `BaseResult`
3. Create your formatter extending `BaseFormatter`
4. Register in the factory - that's it!

### Natural Domain Terminology

Each analyzer uses terminology natural to its domain:

**Quiescence Domain:**
- `staleness_score`, `inactivity_days`, `is_quiescent`
- Natural language: "This ticket appears quiescent..."

**Quality Domain:**
- `quality_score`, `improvement_suggestions`, `needs_improvement`
- Natural language: "This ticket needs improvement..."

## Requirements

- **Python 3.11+**
- **Jira API access** (API token recommended)
- **LLM Provider** (choose one):
  - Anthropic API key for Claude
  - OpenAI API key for GPT models
  - Google API key for Gemini
  - Local Ollama installation

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

## Examples

### Quiescence Analysis Example

```bash
jiraclean --instance personal --project FORGE --analyzer quiescent --max-tickets 5 --dry-run
```

**Output:**
```
🎫 Ticket FORGE-123
┌─────────────────────────────────────────────────────────────────┐
│ Key: FORGE-123                    Assessment: 🟡 QUIESCENT      │
│ Type: Bug                         Staleness: 8.5/10             │
│ Status: In Progress               Inactive Days: 45              │
│ Summary: Fix login issue          Responsible: John Doe          │
└─────────────────────────────────────────────────────────────────┘
```

### Quality Analysis Example

```bash
jiraclean --instance personal --project FORGE --analyzer ticket_quality --max-tickets 5 --dry-run
```

**Output:**
```
🎫 Ticket FORGE-456
┌─────────────────────────────────────────────────────────────────┐
│ Key: FORGE-456                    Assessment: 🔴 NEEDS IMPROVEMENT│
│ Type: Story                       Quality Score: 3/10            │
│ Status: To Do                     Improvements: Add acceptance   │
│ Summary: User dashboard           criteria, Define scope         │
└─────────────────────────────────────────────────────────────────┘
```

## License

MIT License - see [LICENSE](LICENSE) for details.

## Support

- 📚 **Documentation**: Start with our [User Guide](docs/user/README.md)
- 🐛 **Issues**: Report bugs via [GitHub Issues](https://github.com/vacobuilt/jira-cleanup/issues)
- 💬 **Discussions**: Join conversations in [GitHub Discussions](https://github.com/vacobuilt/jira-cleanup/discussions)
- 🤝 **Contributing**: See our [Contributing Guide](docs/developer/contributing.md)

---

**Ready to get started?** Check out our [Quick Start Guide](docs/user/quickstart.md) or run `jiraclean setup` for interactive configuration!
