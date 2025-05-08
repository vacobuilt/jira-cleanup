# Design Decisions Log

## Template Location and Configuration (2025-05-08)

We've implemented a flexible approach to template management based on the following design principles:

1. **User Customizability**: Templates should be easily editable by end users
2. **Persistence**: Customizations should survive package updates
3. **Discoverability**: Template locations should be intuitive and easy to find
4. **Fallbacks**: Default templates should always be available

The implemented solution uses a lookup path system similar to many Unix/Linux applications:

### Template Lookup Path (in order of precedence)
1. User-specific templates: `~/.config/jiraclean/templates/`
2. System-wide templates: `/etc/jiraclean/templates/` (for shared installations)
3. Built-in package templates (as a last resort fallback)

### Template Installation
- Added a setup command `jiraclean setup --install-templates`
- Initial templates are copied to the user's config directory
- Force option (`--force`) to overwrite existing templates

### Rationale
Using `~/.config/jiraclean/` follows the XDG Base Directory Specification used by most modern Linux applications. This directory is:
- User-writable (doesn't require sudo)
- Persists across package upgrades
- Conventional location for configuration files
- Well-supported on Linux, macOS, and adaptable for Windows

The installed templates come directly from the package, ensuring they match the expected format for the current version, but users can freely modify them afterward.

### Package Configuration
Modified pyproject.toml to include template files in the package distribution:
```toml
include = [
    "src/jiraclean/prompts/templates/*.yaml",
    "src/jiraclean/prompts/templates/*.yml"
]
```

This approach means the tool will work out-of-the-box, even if installed directly from GitHub with pipx, while still allowing for user customization.

## Removing Total Ticket Count Functionality (2025-05-08)

We've removed the total ticket count functionality from the iterator interface and implementation due to the following reasons:

1. **Iterator Flexibility**: Not all ticket iterators can know their total count in advance, especially those that:
   - Work with paginated APIs without total count information
   - Stream results dynamically
   - Apply runtime filtering that affects the final count

2. **Implementation Challenges**: The previous implementation attempted to add a `total` attribute to a Python list in `JiraClient.search_issues()`:
   ```python
   # This was causing an error:
   result.total = getattr(issues, 'total', len(result))
   ```
   This design doesn't work because Python lists don't support adding arbitrary attributes.

3. **Simplification**: Removing this functionality simplifies the codebase and removes a potential source of errors, especially when working with different API implementations or data sources.

### Changes Made
- Removed the abstract `total_tickets` property from the `TicketIterator` base class
- Removed dependent properties (`remaining_count` and `progress_percentage`)
- Removed the `_total` field tracking in the `ProjectTicketIterator` class
- Removed the attempt to add a `total` attribute to the search results list

### Impact
- Progress reporting now relies solely on processed count, without reference to a total
- All code paths that might have used total counts now gracefully handle their absence
- The application can work with any iterator implementation, regardless of whether totals are available

This change enhances the robustness of the application by removing assumptions about the availability of total counts, making it compatible with a wider range of data sources and APIs.

## Enhanced Dry Run Output (2025-05-08)

When running the application in dry run mode, it's important to see exactly what would be posted to Jira if the application were running in production mode. We've made improvements to the dry run output to show the complete content of would-be changes:

1. **Improved DryRunJiraClient**: Updated the dry run client to print the exact content that would be posted to Jira in a clearly formatted way:
   ```
   --- WOULD POST TO TICKET-123 ---
   [Full comment text that would be posted]
   --------------------------------------------------
   ```

2. **Better Processor Integration**: Modified the QuiescentTicketProcessor to call the dry run client directly instead of just logging a truncated version of the comment.

These changes allow users to:
- See exactly what would be posted to Jira tickets in production mode
- Verify the correctness and appropriateness of automated comments
- Make informed decisions about whether to run in production mode

The improved output makes the dry run mode much more useful for testing and verification purposes, enhancing the overall user experience and safety of the application.

## Robust LLM Response Handling (2025-05-08)

When working with LLM responses, we encountered issues with JSON formatting, especially when handling multiline strings in the JSON output. The original implementation failed when the LLM included line breaks or control characters in string values, particularly in the `planned_comment` field.

### Problem:
```
Error parsing LLM response: Invalid control character at: line 7 column 56 (char 432)
```

We implemented a more robust solution with two components:

1. **Improved LLM Prompting**: Updated the system prompt to explicitly instruct the LLM on proper JSON formatting:
   ```python
   "system": "You are an expert Jira ticket analyst. Provide JSON output only. For all JSON string values, 
   especially in the planned_comment field, format all text as a single line with no line breaks. 
   If you need to represent a line break in the planned_comment field, use the \\n escape sequence."
   ```

2. **Robust JSON Parsing**: Enhanced the JSON parsing logic to handle common formatting issues:
   - First attempt standard JSON parsing
   - If that fails, apply sanitization to fix common issues:
     - Convert literal newlines in string values to `\n` escape sequences
     - Remove invalid control characters
   - Try parsing again with the sanitized response

This two-pronged approach significantly improves robustness by both preventing issues (better prompting) and gracefully handling them when they occur (better parsing). The result is a more reliable tool that can process a wider variety of LLM responses without failing.

## Package Structure Consolidation (2025-05-08)

We've decided to consolidate the project's package structure to address parallel implementations and configuration mismatches. Currently, the project has:

1. **Multiple package structures**:
   - A flat structure at the src/ root level (main.py, utils/, iterators/, etc.)
   - A namespaced structure under src/jiraclean/ (same modules but with jiraclean namespace)
   - Domain-driven architecture components (domain/, infrastructure/)

2. **Configuration mismatches**:
   - setup.py: Using find_packages pointing to "jira_cleanup"
   - pyproject.toml: Using Poetry with explicit include for "jiraclean"

### Consolidation Decision

We'll standardize on a single, cohesive namespace structure under `jiraclean` for the following reasons:

1. **Namespace Benefits**:
   - Prevents import collisions with other libraries
   - Provides clearer project identity
   - Aligns with modern Python packaging practices
   - Makes imports more explicit and traceable

2. **Poetry as Build System**:
   - More modern and feature-rich than setuptools
   - Better dependency management with explicit lock file
   - Better virtual environment integration
   - Simpler development workflow

3. **Integration Planning**:
   - Domain-driven architecture components will be integrated under the jiraclean namespace
   - This preserves the architectural benefits while maintaining namespace consistency

### Implementation Approach

We've created a detailed migration plan in next_steps.md that outlines:
- Audit and preparation steps
- Package configuration standardization
- Systematic code migration
- Validation and testing procedures
- Documentation updates

This consolidation will improve maintainability, simplify onboarding for new developers, and ensure consistent import patterns throughout the codebase.
