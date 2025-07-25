# Changelog

All notable changes to the Jira Cleanup project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Future enhancements and features will be listed here

## [1.0.0] - 2025-01-25

### Added
- **Multi-Provider LLM Support**: Complete support for Ollama, OpenAI, Anthropic, and Google LLM providers
- **Multi-Instance Jira Support**: Manage multiple Jira instances with easy switching via CLI
- **Clean Architecture Implementation**: Full separation of business logic from infrastructure concerns
- **Advanced Configuration System**: YAML-based configuration with provider-specific validation
- **Beautiful CLI Interface**: Rich console output with Typer-based commands and auto-completion
- **Comprehensive Documentation**: Structured docs/ directory with user, developer, architecture, and changes categories
- **LangChain Integration**: Modern LLM abstraction with factory pattern for provider management
- **Type-Safe Implementation**: Full type hints and proper error handling across all components
- **Dependency Injection**: Clean separation of concerns with injectable dependencies
- **Provider Auto-Detection**: Automatic detection of available LLM providers and dependencies

### Changed
- **Complete Architecture Overhaul**: Migrated from simple script to Clean Architecture with domain-driven design
- **Configuration System**: Enhanced from environment variables to comprehensive YAML-based multi-provider configuration
- **CLI Interface**: Upgraded from basic argparse to modern Typer with Rich formatting
- **LLM Integration**: Evolved from direct Ollama integration to multi-provider LangChain abstraction
- **Documentation Structure**: Reorganized from root-level markdown files to structured docs/ directory
- **Package Structure**: Consolidated to unified `jiraclean` namespace with proper module organization

### Fixed
- **Provider Compatibility**: Resolved API compatibility issues across different LLM providers
- **Type Safety**: Fixed type annotation issues and improved error handling
- **Configuration Validation**: Enhanced validation for provider-specific configuration requirements
- **Documentation Organization**: Improved accessibility and cross-referencing between documentation sections

### Technical Achievements
- **Factory Pattern**: Clean provider abstraction with graceful dependency handling
- **Business Logic Separation**: Pure business logic in `TicketAnalyzer` with no I/O dependencies
- **Unified Interface**: Consistent API across all LLM providers with provider-specific optimizations
- **Error Resilience**: Comprehensive error handling with clear user feedback
- **Extensible Design**: Plugin-ready architecture for future provider additions

## [0.2.0] - 2025-05-08

### Added
- Template location and configuration system with user customization support
- Robust LLM response handling with JSON parsing improvements
- Ticket pre-filtering system for improved efficiency
- Enhanced dry run output showing exact content that would be posted
- Automatic retry mechanism for LLM JSON parsing errors
- Support for user-specific templates in `~/.config/jiraclean/templates/`
- Template installation command: `jiraclean setup --install-templates`

### Changed
- Removed total ticket count functionality from iterator interface for better flexibility
- Improved LLM prompting with explicit JSON formatting instructions
- Enhanced error handling for malformed LLM responses
- Updated template lookup path system (user → system → built-in)

### Fixed
- JSON parsing errors with multiline strings in LLM responses
- Iterator implementation issues with total count tracking
- Template loading and customization workflow

### Removed
- Total ticket count tracking from iterators (was causing implementation issues)
- Hardcoded template paths in favor of configurable system

## [0.1.0] - 2025-05-01

### Added
- Initial project structure with Clean Architecture principles
- Domain-driven design implementation with entities, repositories, and services
- Jira API integration with authentication support
- LLM-powered ticket assessment using Ollama
- Dry-run mode for safe testing
- Command-line interface with comprehensive options
- Environment-based configuration system
- Template-based prompt system for LLM interactions
- Project-based ticket iteration and filtering
- Quiescent ticket processing with automated actions

### Core Features
- **Ticket Assessment**: Rule-based and LLM-powered evaluation of ticket quiescence
- **Automated Actions**: Comment generation and posting to Jira tickets
- **Safety Controls**: Dry-run mode and force dry-run environment variable
- **Flexible Configuration**: Environment variables, command-line options, and template customization
- **Extensible Architecture**: Plugin-ready design for new iterators, processors, and LLM providers

### Technical Implementation
- Clean Architecture with domain, application, and infrastructure layers
- Repository pattern for data access abstraction
- Strategy pattern for ticket selection and processing
- Dependency injection for loose coupling
- Comprehensive error handling and logging

### Documentation
- README with project overview and usage instructions
- Quick start guide for immediate setup
- Installation guide with Poetry and pipx support
- Architecture analysis and design decisions documentation

## Development Milestones

### Package Structure Evolution
The project has evolved through several package structure iterations:

1. **Initial Flat Structure**: Simple src/ layout with direct module imports
2. **Parallel Structures**: Both flat and namespaced structures coexisting
3. **Consolidation Phase**: Moving toward unified `jiraclean` namespace (in progress)

### Architecture Maturity
The architecture has progressed through these stages:

1. **Basic Structure**: Simple script-based approach
2. **Layered Architecture**: Introduction of domain and infrastructure layers
3. **Clean Architecture**: Full implementation of Clean Architecture principles
4. **Domain-Driven Design**: Rich domain model with business logic encapsulation

## Migration Notes

### From 0.1.x to 0.2.x
- Template system has been redesigned - existing custom templates may need to be moved to the new location
- Iterator interface has changed - custom iterators should be updated to remove total count functionality
- LLM response format has been improved - existing prompt templates are compatible but may benefit from updates

### Upcoming Changes (0.3.x)
- Package structure consolidation will require import path updates
- Dependency injection container introduction may affect manual dependency wiring
- Use case implementation will change application orchestration patterns

## Contributing

We welcome contributions! Please see our [Contributing Guide](../developer/contributing.md) for details on:
- Development setup and workflow
- Code standards and quality requirements
- Pull request process and review guidelines
- Architecture principles and extension points

## Support

For questions, issues, or feature requests:
- Check the [User Documentation](../user/) for usage help
- Review the [Developer Documentation](../developer/) for technical details
- Submit issues through GitHub Issues
- Participate in discussions through GitHub Discussions

## License

This project is licensed under the MIT License - see the [LICENSE](../../LICENSE) file for details.
