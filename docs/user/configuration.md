# Configuration Guide

This guide explains how to configure Jira Cleanup for your environment.

## Environment Variables

Create a `.env` file in the project directory or in your home directory (`~/.env`) with your Jira credentials and configuration:

```bash
# Copy the example file
cp .env.example .env

# Edit with your information
nano .env  # or use your preferred editor
```

## Configuration Settings

The `.env` file should contain the following settings:

### Jira Authentication

```ini
# Jira Authentication
JIRA_URL=https://your-instance.atlassian.net
JIRA_USER=your-email@example.com
JIRA_TOKEN=your-api-token
JIRA_AUTH_METHOD=token
```

**Getting a Jira API Token:**
1. Go to your Atlassian Account Settings
2. Navigate to Security → API tokens
3. Create a new API token
4. Copy the token to your `.env` file

### Project Settings

```ini
# Project Settings
JIRA_CLEANUP_PROJECT=PROJ              # Default project to process
JIRA_CLEANUP_DRY_RUN=true             # Default to dry run for safety
JIRA_CLEANUP_MAX_TICKETS=50           # Limit number of tickets to process
```

### LLM Settings

```ini
# LLM Settings (optional)
OLLAMA_URL=http://localhost:11434      # Ollama server URL
LLM_MODEL=llama3.2:latest             # Model to use for assessment
```

### Logging

```ini
# Logging
JIRA_CLEANUP_LOG_LEVEL=INFO           # DEBUG, INFO, WARNING, ERROR
```

## Ollama Setup

To use the LLM assessment capabilities, you need to have Ollama running with the correct models:

### Installation

1. Install Ollama from [https://ollama.ai/](https://ollama.ai/)
2. Pull the required models:
   ```bash
   ollama pull llama3.2:latest
   ```
3. Ensure Ollama is running:
   ```bash
   ollama serve
   ```

### Model Selection

Different models provide different capabilities:

- **llama3.2:latest** - Good balance of speed and accuracy
- **llama3.2:3b** - Faster, less accurate
- **llama3.2:70b** - More accurate, slower

## Safety Configuration

### Force Dry Run

For additional safety, you can set `FORCE_DRY_RUN=true` in your `.env` file. This will force the tool to run in dry run mode regardless of command line arguments, preventing accidental production runs.

```ini
# Safety setting - prevents accidental production runs
FORCE_DRY_RUN=true
```

To disable this safety and allow production runs:

```ini
FORCE_DRY_RUN=false
```

### Environment-Specific Configuration

For different environments (development, staging, production), consider creating separate `.env` files:

```bash
# Development environment
.env.development

# Staging environment  
.env.staging

# Production environment
.env.production
```

Specify the environment file at runtime:

```bash
python -m jiraclean --env-file .env.production
```

## Template Customization

Jira Cleanup uses YAML templates for LLM prompts that can be customized:

### Installing Templates

```bash
# Install default templates to user directory
jiraclean setup --install-templates

# Force overwrite existing templates
jiraclean setup --install-templates --force
```

### Template Locations

Templates are loaded in this order of precedence:

1. **User templates**: `~/.config/jiraclean/templates/`
2. **System templates**: `/etc/jiraclean/templates/` (if available)
3. **Built-in templates**: Package defaults

### Customizing Templates

Edit templates in `~/.config/jiraclean/templates/`:

- `quiescent_assessment.yaml` - Controls how tickets are assessed
- `closure_recommendation.yaml` - Controls closure recommendations

Example template structure:

```yaml
system: |
  You are an expert Jira ticket analyst...

user: |
  Analyze this ticket:
  Key: {ticket_key}
  Summary: {summary}
  ...
```

## Command Line Options

Configuration can also be provided via command line arguments:

```bash
# Override project setting
python -m jiraclean --project PROJECT_KEY

# Override dry run setting
python -m jiraclean --dry-run

# Override max tickets
python -m jiraclean --max-tickets 20

# Disable LLM assessment
python -m jiraclean --no-llm

# Use specific environment file
python -m jiraclean --env-file /path/to/.env

# Set log level
python -m jiraclean --log-level DEBUG
```

## Validation

To validate your configuration:

```bash
# Test connection to Jira
python -m jiraclean --project TEST --max-tickets 1 --dry-run

# Test LLM connection (if configured)
python -m jiraclean --project TEST --max-tickets 1 --with-llm --dry-run
```

## Troubleshooting

### Connection Issues

If you encounter Jira connection issues:

1. Verify your Jira URL and credentials in the `.env` file
2. Check your API token hasn't expired
3. Ensure your user has sufficient permissions in Jira
4. Test with a simple curl command:
   ```bash
   curl -u your-email@example.com:your-api-token \
        https://your-instance.atlassian.net/rest/api/2/myself
   ```

### LLM Issues

If LLM assessment is not working:

1. Ensure Ollama is running: `ollama serve`
2. Verify you have the correct model downloaded: `ollama list`
3. Check the OLLAMA_URL in your `.env` file
4. Test Ollama directly:
   ```bash
   curl http://localhost:11434/api/generate -d '{
     "model": "llama3.2:latest",
     "prompt": "Hello, world!"
   }'
   ```

### Permission Issues

If you encounter permission errors:

1. Ensure your Jira user has the necessary permissions:
   - Browse projects
   - Add comments to issues
   - Edit issues (if using status transitions)
2. Check project-specific permissions
3. Verify API token scope and permissions

## Security Best Practices

1. **Never commit `.env` files** to version control
2. **Use API tokens** instead of passwords
3. **Limit API token scope** to necessary permissions
4. **Rotate API tokens** regularly
5. **Use separate tokens** for different environments
6. **Store sensitive configuration** in secure vaults for production deployments
