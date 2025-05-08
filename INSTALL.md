# Installation Guide

This document explains how to install and set up the Jira Cleanup tool using Poetry for development and pipx for system-wide installation.

## Prerequisites

- Python 3.11 or newer
- [pipx](https://pypa.github.io/pipx/) for isolated application installation
- [Poetry](https://python-poetry.org/) for dependency management

If you don't have pipx or Poetry installed, you can install them with:

```bash
# Install pipx
python -m pip install --user pipx
python -m pipx ensurepath

# Install Poetry
curl -sSL https://install.python-poetry.org | python3 -
```

## Development Installation

For development work, clone the repository and use Poetry to set up the environment:

```bash
# Clone the repository
git clone https://github.com/vacobuilt/jira-cleanup.git
cd jira-cleanup

# Install dependencies with Poetry
poetry install

# Activate the virtual environment
poetry shell

# Run the application in development mode
jiraclean --help
```

## System Installation with pipx

For regular usage, you can install directly from the repository using pipx:

```bash
# Install from GitHub
pipx install git+https://github.com/vacobuilt/jira-cleanup.git

# Or install from your local copy
pipx install .
```

This will make the `jiraclean` command available system-wide without affecting your Python environment.

## Configuration

Before using Jira Cleanup, you need to set up your configuration:

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit the `.env` file with your Jira credentials and settings.

## Customizing Templates

Jira Cleanup uses YAML templates for LLM prompts that can be customized:

1. Install the default templates:
   ```bash
   jiraclean setup --install-templates
   ```

2. Edit templates in `~/.config/jiraclean/templates/`

Templates control how the LLM assesses and responds to tickets. They're loaded in this order of precedence:
1. User templates (`~/.config/jiraclean/templates/`)
2. System templates (`/etc/jiraclean/templates/`) - if available
3. Built-in default templates (package defaults)

## Updating

### Development Environment

To update a development installation:

```bash
git pull
poetry install
```

### System Installation

To update a pipx installation:

```bash
# Update from GitHub
pipx upgrade jira-cleanup

# Or reinstall from your updated local copy
pipx uninstall jira-cleanup
pipx install .
```

After updating, you may need to reinstall templates with:
```bash
jiraclean setup --install-templates --force
```

## Troubleshooting

If you encounter issues with the installation:

1. Ensure you're using Python 3.11 or newer:
   ```bash
   python --version
   ```

2. Update pipx and Poetry:
   ```bash
   python -m pip install --user -U pipx
   poetry self update
   ```

3. Clear Poetry's cache if needed:
   ```bash
   poetry cache clear --all pypi
   ```
