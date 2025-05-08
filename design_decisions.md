# Design Decisions

This document records important design decisions and rationales for the Jira Cleanup project.

## Table of Contents
1. [Prompt Management](#prompt-management)
2. [Client Architecture](#client-architecture)
3. [Safety Controls](#safety-controls)

## Prompt Management

### External Storage of Prompts (2025-05-08)

**Decision**: Store all LLM prompts in external YAML files instead of hardcoding them in the Python code.

**Rationale**:
- Separation of concerns: LLM prompts are effectively content, not code
- Improved maintainability: Non-developers can edit prompts without touching code
- Version control: Prompt changes can be tracked separately from code changes
- Flexibility: Different prompt versions can be easily swapped or A/B tested

**Implementation**:
- Created a `PromptRegistry` class to manage loading and rendering templates
- Used YAML format for easy reading and editing of templates
- Stored templates in `prompts/templates` directory
- Added variable detection and validation to ensure all required variables are provided
- Implemented fast-fail error handling for missing templates or variables

## Client Architecture

### Concrete Client with Dry Run Mode (2025-05-08)

**Decision**: Use a single concrete `JiraClient` class with a subclass `DryRunJiraClient` instead of an abstract interface.

**Rationale**:
- Simplifies the architecture by reducing abstractions
- Both clients share identical read behavior
- Only write operations need to be simulated in dry run mode
- Factory function provides the appropriate client based on configuration

**Implementation**:
- Implemented `DryRunJiraClient` as a subclass of `JiraClient`
- Override only the methods that modify Jira (add_comment, transition_issue, etc.)
- Created a factory function `create_jira_client()` to provide the appropriate implementation
- Dry run client logs what would have happened instead of making API calls

## Safety Controls

### Force Dry Run Mode (2025-05-08)

**Decision**: Add a `FORCE_DRY_RUN` environment variable that enforces dry run mode.

**Rationale**:
- Provides an extra safety mechanism for production environments
- Prevents accidental live runs that could modify tickets
- Allows for system-wide configuration in shared environments
- Complements the existing `--dry-run` command-line option

**Implementation**:
- Added `FORCE_DRY_RUN` to the environment configuration
- Modified the argument parser to use both `JIRA_CLEANUP_DRY_RUN` and `FORCE_DRY_RUN` for the default
- Added validation that prevents live mode when `FORCE_DRY_RUN` is enabled
- Added documentation in the example .env file
