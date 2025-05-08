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

## Documentation

- [Quick Start Guide](quickstart.md) - Step-by-step instructions for running the tool in dry run and production modes
- [Architecture Analysis](jira_cleanup_architecture_analysis.md) - Detailed analysis of the project architecture with recommendations
- [Code Recommendations](jira_cleanup_code_recommendations.md) - Concrete implementation examples for architectural improvements
- [Design Decisions](design_decisions.md) - Record of important design decisions and rationales
- [Next Steps](next_steps.md) - Implementation roadmap with phases and priorities

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/vacobuilt/jira-cleanup.git
   cd jira-cleanup
   ```

2. Install the package and dependencies:
   ```bash
   pip install -e .
   ```

   Or install dependencies directly:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

### Environment Variables

Create a `.env` file in the project directory or in your home directory (`~/.env`) with your Jira credentials and configuration:

```bash
# Copy the example file
cp .env.example .env

# Edit with your information
nano .env  # or use your preferred editor
```

The `.env` file should contain the following settings:

```ini
# Jira Authentication
JIRA_URL=https://your-instance.atlassian.net
JIRA_USER=your-email@example.com
JIRA_TOKEN=your-api-token
JIRA_AUTH_METHOD=token

# Project Settings
JIRA_CLEANUP_PROJECT=PROJ
JIRA_CLEANUP_DRY_RUN=true

# LLM Settings
OLLAMA_URL=http://localhost:11434
LLM_MODEL=llama3.2:latest

# Logging
JIRA_CLEANUP_LOG_LEVEL=INFO
```

### Ollama Setup

To use the LLM assessment capabilities, you need to have Ollama running with the correct models:

1. Install Ollama from [https://ollama.ai/](https://ollama.ai/)
2. Pull the required models:
   ```bash
   ollama pull llama3.2:latest
   ```
3. Ensure Ollama is running:
   ```bash
   ollama serve
   ```

## Usage

Run the tool with your configuration:

```bash
# Basic usage with default settings from .env
python -m jira_cleanup

# Process a specific project
python -m jira_cleanup --project PROJECT_KEY

# Run without making changes to Jira
python -m jira_cleanup --dry-run

# Limit number of tickets to process
python -m jira_cleanup --max-tickets 20

# Disable LLM assessment
python -m jira_cleanup --no-llm

# Use a specific .env file
python -m jira_cleanup --env-file /path/to/.env
```

### Example Commands

```bash
# Test run on 10 tickets without making changes
python -m jira_cleanup --project PROJ --max-tickets 10 --dry-run

# Process all tickets in a project with LLM assessment and take action
python -m jira_cleanup --project PROJ --with-llm
```

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

## Development

### Project Structure

```
jira_cleanup/
├── src/
│   ├── __init__.py
│   ├── main.py               # CLI entry point
│   ├── domain/               # Domain layer (core business logic)
│   │   ├── entities/         # Business objects
│   │   ├── repositories/     # Data access interfaces 
│   │   └── services/         # Domain services
│   ├── infrastructure/       # External systems implementations
│   │   ├── repositories/     # Repository implementations
│   │   └── services/         # Service implementations
│   ├── jirautil/             # Jira API interface
│   │   ├── client.py         # Jira client implementation
│   │   └── exceptions.py     # Custom exceptions
│   ├── iterators/            # Ticket selection strategies
│   │   ├── base.py           # Base iterator interface
│   │   └── project.py        # Project-based iterator
│   ├── processors/           # Ticket processing logic
│   │   ├── base.py           # Base processor interface
│   │   └── quiescent.py      # Quiescent ticket processor
│   ├── llm/                  # LLM integration
│   │   └── assessment.py     # LLM assessment logic
│   ├── prompts/              # LLM prompt templates
│   └── utils/                # Utility functions
├── .env.example              # Example environment config
├── requirements.txt          # Project dependencies
├── setup.py                  # Package installation
├── quickstart.md             # Quick start guide
└── README.md                 # This file
```

### Extending the Tool

You can extend the functionality by:

1. Creating new ticket iterators in `src/iterators/`
2. Adding new processors in `src/processors/`
3. Enhancing LLM prompts in `src/prompts/templates/`
4. Implementing new domain services in `src/domain/services/`

## Requirements

- Python 3.11+
- Jira Python library
- PyYAML
- Python-dotenv
- SQLAlchemy (for caching and tracking)
- Optional: Ollama for LLM-powered analysis

## License

MIT License
