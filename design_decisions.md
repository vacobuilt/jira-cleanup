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
