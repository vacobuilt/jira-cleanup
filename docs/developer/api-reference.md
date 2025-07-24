# API Reference

This document provides detailed API documentation for the Jira Cleanup project.

> **Note**: This API reference is currently being developed. For now, please refer to the source code and docstrings for detailed API information.

## Core Modules

### Domain Layer

#### Entities

**`jiraclean.domain.entities.ticket.Ticket`**
- Core business entity representing a Jira ticket
- Contains ticket metadata and business logic methods
- Methods: `is_quiescent()`, `is_stale()`, `has_recent_activity()`

**`jiraclean.domain.entities.assessment.Assessment`**
- Represents the result of ticket assessment
- Contains quiescence determination and justification

#### Repositories

**`jiraclean.domain.repositories.ticket_repository.TicketRepository`**
- Abstract interface for ticket data access
- Methods: `get_by_key()`, `search()`, `update()`

**`jiraclean.domain.repositories.comment_repository.CommentRepository`**
- Abstract interface for comment operations
- Methods: `add_comment()`, `get_comments()`

#### Services

**`jiraclean.domain.services.quiescence_evaluator.QuiescenceEvaluator`**
- Core business logic for determining ticket quiescence
- Method: `evaluate(ticket) -> Tuple[bool, str, Dict]`

**`jiraclean.domain.services.comment_generator.CommentGenerator`**
- Generates appropriate comments for tickets
- Method: `generate_quiescence_comment(ticket, justification) -> str`

### Infrastructure Layer

#### Repository Implementations

**`jiraclean.infrastructure.repositories.jira_ticket_repository.JiraTicketRepository`**
- Jira-based implementation of TicketRepository
- Handles direct Jira API interactions for ticket operations

**`jiraclean.infrastructure.repositories.jira_comment_repository.JiraCommentRepository`**
- Jira-based implementation of CommentRepository
- Handles comment creation and retrieval via Jira API

#### Service Implementations

**`jiraclean.infrastructure.services.ollama_llm_service.OllamaLlmService`**
- Ollama-based implementation of LlmService
- Provides LLM-powered ticket assessment capabilities

### Application Layer

#### Iterators

**`jiraclean.iterators.base.TicketIterator`**
- Abstract base class for ticket selection strategies
- Method: `__iter__() -> Iterator[Ticket]`

**`jiraclean.iterators.project.ProjectTicketIterator`**
- Concrete implementation for project-based ticket iteration
- Supports filtering and pagination

#### Processors

**`jiraclean.processors.base.TicketProcessor`**
- Abstract base class for ticket processing strategies
- Method: `process(ticket) -> Dict[str, Any]`

**`jiraclean.processors.quiescent.QuiescentTicketProcessor`**
- Concrete implementation for quiescent ticket processing
- Handles assessment and action taking

### Utility Modules

#### Configuration

**`jiraclean.utils.config`**
- Configuration management utilities
- Environment variable handling and validation

#### Jira Utilities

**`jiraclean.jirautil.client.JiraClient`**
- Main Jira API client
- Handles authentication and API interactions

**`jiraclean.jirautil.dry_run_client.DryRunJiraClient`**
- Dry-run implementation of Jira client
- Simulates operations without making actual changes

## CLI Interface

### Main Entry Point

**`jiraclean.main.main()`**
- Primary CLI entry point
- Handles argument parsing and application orchestration

### Command Line Arguments

- `--project`: Specify Jira project key
- `--dry-run`: Run in simulation mode
- `--max-tickets`: Limit number of tickets to process
- `--with-llm`: Enable LLM assessment
- `--no-llm`: Disable LLM assessment
- `--env-file`: Specify environment file path
- `--log-level`: Set logging level

## Extension Points

### Adding New Iterators

1. Inherit from `TicketIterator`
2. Implement `__iter__()` method
3. Register in iterator factory

### Adding New Processors

1. Inherit from `TicketProcessor`
2. Implement `process()` method
3. Add configuration options as needed

### Adding New LLM Providers

1. Implement `LlmService` interface
2. Add configuration handling
3. Register in service factory

## Error Handling

### Exception Hierarchy

**`jiraclean.jirautil.exceptions.JiraCleanupError`**
- Base exception for all application errors

**`jiraclean.jirautil.exceptions.JiraConnectionError`**
- Raised when Jira API connection fails

**`jiraclean.jirautil.exceptions.ConfigurationError`**
- Raised when configuration is invalid

## Configuration

### Environment Variables

See [Configuration Guide](../user/configuration.md) for complete list of environment variables.

### Template System

Templates are loaded from:
1. User directory: `~/.config/jiraclean/templates/`
2. System directory: `/etc/jiraclean/templates/`
3. Package defaults

## Future API Additions

This API reference will be expanded to include:

- Complete method signatures with type hints
- Parameter descriptions and examples
- Return value documentation
- Exception handling details
- Usage examples for each module
- Integration patterns and best practices

For the most current API information, please refer to the source code docstrings and type hints.
