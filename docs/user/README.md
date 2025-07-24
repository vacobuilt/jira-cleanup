# Jira Cleanup

A configurable, policy-based tool for automated Jira ticket governance and lifecycle management.

## Purpose

The Jira Cleanup project provides a robust framework for implementing governance policies across your Jira projects. It allows you to:

1. **Automate governance checks** across configurable sets of Jira tickets
2. **Apply customizable policies** to ensure tickets follow organizational standards
3. **Take automated actions** based on ticket state and activity
4. **Reduce ticket clutter** by properly handling stalled or abandoned work

This tool helps maintain a clean and efficient Jira workspace by identifying and addressing tickets that need attention, providing accountability, and closing tickets that are no longer relevant.

## Key Features

- **Configurable Ticket Selection**: Define which tickets to evaluate based on project, status, labels, or custom JQL
- **Customizable Governance Policies**: Create rules that define proper ticket lifecycle management
- **Automated Actions**: Comment, assign, transition status, or close tickets based on policy evaluation
- **Tiered Response System**: Escalate actions based on ticket age and previous interactions
- **Integration with Jira API**: Uses the Python Jira library for direct interaction with your Jira instance
- **Local LLM Assessment**: Optional AI-powered ticket analysis for intelligent decision-making

## How It Works

1. **Selection Phase**: The tool fetches tickets matching your criteria
2. **Analysis Phase**: Each ticket is examined for quiescence:
   - Using rules like age, updates, and status
   - Optionally using LLM analysis to make intelligent assessments
3. **Action Phase**: Based on the analysis, tickets may receive:
   - Comments requesting updates
   - Status transitions
   - Other configured actions
4. **Reporting Phase**: Summary of actions taken and stats

## Requirements

- Python 3.11+
- Jira Python library
- PyYAML
- Python-dotenv
- SQLAlchemy (for caching and tracking)
- Optional: Ollama for LLM-powered analysis

## Getting Started

1. **[Install the tool](installation.md)** - Set up Jira Cleanup on your system
2. **[Follow the Quick Start Guide](quickstart.md)** - Get up and running in minutes
3. **[Configure for your environment](configuration.md)** - Customize settings for your Jira instance

## Project Structure

```
jira_cleanup/
├── src/
│   ├── jiraclean/            # Main application package
│   │   ├── domain/           # Core business logic and entities
│   │   ├── infrastructure/   # External systems implementations
│   │   ├── jirautil/         # Jira API interface
│   │   ├── iterators/        # Ticket selection strategies
│   │   ├── processors/       # Ticket processing logic
│   │   ├── llm/              # LLM integration
│   │   └── prompts/          # LLM prompt templates
│   └── main.py               # CLI entry point
├── docs/                     # Documentation
├── .env.example              # Example environment config
├── requirements.txt          # Project dependencies
└── pyproject.toml            # Package configuration
```

## License

MIT License

## Support

For questions, issues, or contributions, please visit the project repository or refer to our [developer documentation](../developer/).
