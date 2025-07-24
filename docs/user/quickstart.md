# Jira Cleanup Tool - Quick Start Guide

This guide provides step-by-step instructions for running the Jira Cleanup tool in both dry run (testing) and production modes.

## Prerequisites

- Python 3.11 or higher
- Jira API access token
- (Optional) Ollama for LLM-powered assessments

## Setup

### Option 1: Install with pipx (Recommended)

1. Install directly with pipx:
   ```bash
   pipx install git+https://github.com/vacobuilt/jira-cleanup.git
   ```

2. Create and configure your `.env` file:
   ```bash
   # Copy the example file (if you have the repo)
   cp .env.example .env
   
   # Or create a new .env file in your home directory
   nano ~/.env  # or vim, code, etc.
   ```

3. Update the `.env` file with your Jira credentials:
   ```ini
   # Jira Authentication
   JIRA_URL=https://your-instance.atlassian.net
   JIRA_USER=your-email@example.com
   JIRA_TOKEN=your-api-token
   JIRA_AUTH_METHOD=token
   
   # Default Project Settings
   JIRA_CLEANUP_PROJECT=YOUR_PROJECT
   JIRA_CLEANUP_DRY_RUN=true  # Default to dry run for safety
   
   # Optional LLM Settings (only needed for LLM assessments)
   OLLAMA_URL=http://localhost:11434
   LLM_MODEL=llama3.2:latest
   ```

### Option 2: Development Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/jira-cleanup.git
   cd jira-cleanup
   ```

2. Install dependencies:
   ```bash
   pip install -e .
   # or
   pip install -r requirements.txt
   ```

3. Create and configure your `.env` file:
   ```bash
   # Copy the example file
   cp .env.example .env
   
   # Edit with your favorite editor
   nano .env  # or vim, code, etc.
   ```

4. Update the `.env` file with your Jira credentials:
   ```ini
   # Jira Authentication
   JIRA_URL=https://your-instance.atlassian.net
   JIRA_USER=your-email@example.com
   JIRA_TOKEN=your-api-token
   JIRA_AUTH_METHOD=token
   
   # Default Project Settings
   JIRA_CLEANUP_PROJECT=PROJ
   JIRA_CLEANUP_DRY_RUN=true  # Default to dry run for safety
   
   # Optional LLM Settings (only needed for LLM assessments)
   OLLAMA_URL=http://localhost:11434
   LLM_MODEL=llama3.2:latest
   ```

## Running in Dry Run Mode (Safe Testing)

Dry run mode allows you to see what actions would be taken without actually modifying any tickets in Jira. This is perfect for testing your configuration and understanding the tool's behavior.

### 🎯 Modern CLI with Beautiful Rich Output

The new Typer-based CLI provides beautiful, color-coded output with Rich formatting:

```bash
# 🎨 Beautiful Rich output with prominent ticket display
jiraclean main-command --project PROJECT_KEY --dry-run

# 🚀 Interactive setup wizard
jiraclean setup

# ⚙️ Configuration management
jiraclean config list
jiraclean config show

# 📋 Get help with beautiful formatting
jiraclean --help
jiraclean main-command --help
```

### Basic Dry Run

```bash
# For pipx installation (recommended) - Modern CLI
jiraclean main-command --project PROJECT_KEY --dry-run

# Legacy CLI (still supported)
jiraclean --project PROJECT_KEY --dry-run

# For development installation
source venv/bin/activate
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
python -m jiraclean.cli.main main-command --project PROJECT_KEY --dry-run
```

### Dry Run with Limited Tickets

```bash
# Process only 10 tickets with beautiful Rich formatting
jiraclean main-command --project PROJECT_KEY --max-tickets 10 --dry-run --no-llm
```

### Dry Run with LLM Assessment

If you have Ollama set up and running:

```bash
# Use LLM assessment with Rich-formatted output
jiraclean main-command --project PROJECT_KEY --with-llm --dry-run
```

### 🎨 Rich Output Example (New CLI)

The new CLI provides beautiful, structured output with Rich formatting:

```
╭───────────────────────────────────────────── 🚀 Jira Cleanup Processing ─────────────────────────────────────────────╮
│                                                                                                                      │
│             Mode: 🔍 DRY RUN MODE                                                                                    │
│                                                                                                                      │
│          Project: PROJ                                                                                               │
│                                                                                                                      │
│      Max Tickets: 10                                                                                                 │
│                                                                                                                      │
│              LLM: ✅ LLM Assessment                                                                                  │
│                                                                                                                      │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

ℹ️  Processing 10 tickets from project PROJ

╭─────────────────────────────────────────── 🎫 Ticket PROJ-123 ───────────────────────────────────────────╮
│                                                                                                           │
│         Key: PROJ-123                    │                                                               │
│        Type: Task                        │                                                               │
│      Status: Open                        │                                                               │
│    Priority: Medium                      │                                                               │
│    Assignee: john.doe@company.com        │                                                               │
│    Reporter: jane.smith@company.com      │                                                               │
│     Summary: Update documentation for API changes                                                        │
│                                                                                                           │
│  Assessment: 🟡 QUIESCENT                                                                                │
│      Reason: No activity for 20 days, needs attention                                                    │
│ Responsible: john.doe@company.com                                                                         │
│      Action: Add reminder comment                                                                         │
│                                                                                                           │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────────╯

✅ Command completed successfully
```

### Legacy Output Example (Original CLI)

The original CLI still works and provides text-based output:

```
Processing tickets for project PROJ
LLM assessment: Enabled
Dry run mode: True
--------------------------------------------------

Ticket 1: PROJ-123
  Type: Task
  Status: Open
  Summary: Update documentation for API changes
  Assessment: Quiescent
  [WOULD ADD COMMENT]: "This ticket appears to have been inactive for 20 days. 
   Is there any update on the progress? If there's no response within 7 days, 
   this ticket may be closed."
--------------------------------------------------

Ticket 2: PROJ-124
...
```

## Running in Production Mode

When you're ready to take real actions on tickets (adding comments, changing statuses, etc.), you can run the tool in production mode.

> ⚠️ **IMPORTANT**: Production mode will make actual changes to your Jira tickets. Always run in dry run mode first to verify the expected behavior.

### Basic Production Run

```bash
# Omit the --dry-run flag to run in production mode
python -m jira_cleanup --project PROJECT_KEY
```

### Production Run for Specific Project

```bash
# Run against a specific project
python -m jira_cleanup --project HR
```

### Production Run with LLM Assessment

```bash
# Use LLM for more intelligent assessment
python -m jira_cleanup --project SALES --with-llm
```

### Full Production Run (All Options)

```bash
# Complete example with all common options
python -m jira_cleanup --project DEV --with-llm --log-level INFO
```

### Output Example (Production Mode)

When running in production mode, you'll see output like:

```
Processing tickets for project PROJ
LLM assessment: Enabled
Dry run mode: False
--------------------------------------------------

Ticket 1: PROJ-123
  Type: Task
  Status: Open
  Summary: Update documentation for API changes
  Assessment: Quiescent
  Action: Comment added
--------------------------------------------------

Ticket 2: PROJ-124
...
```

## Safety Features

### Force Dry Run Environment Variable

For additional safety, you can set `FORCE_DRY_RUN=true` in your `.env` file. This will force the tool to run in dry run mode regardless of command line arguments, preventing accidental production runs.

To disable this safety and allow production runs:

```bash
# Edit your .env file
FORCE_DRY_RUN=false
```

### Environment-Specific Configuration

For different environments (development, staging, production), consider creating separate `.env` files and specifying them at runtime:

```bash
# Using a specific environment file
python -m jira_cleanup --project PROJECT_KEY --env-file .env.production
```

## Troubleshooting

### Connection Issues

If you encounter Jira connection issues:

1. Verify your Jira URL and credentials in the `.env` file
2. Check your API token hasn't expired
3. Ensure your user has sufficient permissions in Jira

### LLM Issues

If LLM assessment is not working:

1. Ensure Ollama is running: `ollama serve`
2. Verify you have the correct model downloaded: `ollama pull llama3.2:latest`
3. Check the OLLAMA_URL in your `.env` file

### Logging

Increase logging level for more detailed output:

```bash
python -m jira_cleanup --project PROJECT_KEY --log-level DEBUG
```

## Next Steps

- Create custom policies for different types of governance
- Schedule regular runs using cron or a similar scheduler
- Integrate with notification systems to alert teams about inactive tickets
