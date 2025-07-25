# Jira Cleanup Enhancement Development Plan

## Overview
Enhance the Jira Cleanup tool with a modern CLI interface using Typer and beautiful output formatting using Rich. Focus on improving user experience, configuration management, and visual distinction between original tickets and feedback.

## Phase 1: CLI Enhancement with Typer

### 1.1 Core CLI Migration
- [ ] Replace argparse with Typer in `src/jiraclean/main.py`
- [ ] Implement Typer app with proper command structure
- [ ] Add rich help text and command descriptions
- [ ] Maintain backward compatibility with existing command-line options
- [ ] Add auto-completion support

### 1.2 Command Structure
- [ ] Main command: `jiraclean` (default ticket processing)
- [ ] Subcommand: `jiraclean setup` (configuration setup)
- [ ] Subcommand: `jiraclean config` (show current configuration)
- [ ] Subcommand: `jiraclean validate` (validate configuration)
- [ ] Add `--help` improvements with examples

### 1.3 Enhanced Options
- [ ] Add `--interactive` mode for guided setup
- [ ] Add `--output-format` option (table, json, yaml)
- [ ] Add `--filter` options for advanced ticket filtering
- [ ] Add `--profile` support for multiple configurations

## Phase 2: Rich Output Implementation

### 2.1 Core Rich Integration
- [ ] Create `src/jiraclean/ui/` module for Rich components
- [ ] Implement Rich Console singleton
- [ ] Replace all print statements with Rich equivalents
- [ ] Add proper error formatting with Rich

### 2.2 Ticket Display Enhancement
- [ ] **Original Ticket Highlighting**: Use Rich panels/boxes to make original tickets stand out
- [ ] **Feedback Distinction**: Use different colors/styles for LLM feedback vs original ticket data
- [ ] Create ticket card component with:
  - [ ] Ticket key prominently displayed
  - [ ] Status with color coding
  - [ ] Priority with icons/colors
  - [ ] Summary with proper text wrapping
  - [ ] Assignee and reporter information

### 2.3 Progress and Status Indicators
- [ ] Add progress bars for ticket processing
- [ ] Add spinners for API calls and LLM processing
- [ ] Add status indicators (✓, ✗, ⚠, ℹ) for different states
- [ ] Add live status updates during processing

### 2.4 Interactive Elements
- [ ] Add confirmation prompts for production mode
- [ ] Add interactive project selection
- [ ] Add interactive configuration wizard
- [ ] Add "press any key to continue" for large outputs

## Phase 3: Enhanced Configuration Management

### 3.1 YAML Configuration System
- [ ] Replace `.env` with YAML configuration file (`~/.config/jiraclean/config.yaml`)
- [ ] Support multiple named Jira instances in single config file
- [ ] Add default instance selection
- [ ] Maintain backward compatibility with `.env` files
- [ ] Add configuration schema validation with pyyaml

### 3.2 Multi-Instance Jira Support
- [ ] Configuration structure for multiple Jira instances:
  ```yaml
  jira:
    default: "production"
    instances:
      production:
        url: "https://company.atlassian.net"
        username: "user@company.com"
        token: "token"
      staging:
        url: "https://staging.atlassian.net"
        username: "user@company.com"
        token: "token"
  ```
- [ ] Add `--instance` CLI option to select specific instance
- [ ] Add instance listing and validation commands
- [ ] Add instance connection testing

### 3.3 Configuration Management
- [ ] Add `jiraclean config init` command for setup wizard
- [ ] Add `jiraclean config list` to show all instances
- [ ] Add `jiraclean config test <instance>` for connection testing
- [ ] Add `jiraclean config set-default <instance>` command
- [ ] Add configuration validation and health checks
- [ ] Support environment variable overrides for CI/CD

## Phase 4: Output Formatting and Visualization

### 4.1 Ticket Processing Output
- [ ] **Ticket Cards**: Rich-formatted cards for each ticket with:
  - [ ] **Header**: Ticket key, type, status (with colors)
  - [ ] **Content**: Summary, description preview
  - [ ] **Metadata**: Assignee, reporter, dates, priority
  - [ ] **Assessment**: LLM feedback in distinct styling
  - [ ] **Actions**: What would be done (dry-run) or was done

### 4.2 Summary and Statistics
- [ ] Add processing summary with Rich tables
- [ ] Add statistics dashboard (tickets processed, actions taken, etc.)
- [ ] Add time tracking for operations
- [ ] Add success/failure rate indicators

### 4.3 Error Handling and Logging
- [ ] Rich-formatted error messages with context
- [ ] Structured logging with Rich integration
- [ ] Error recovery suggestions
- [ ] Debug mode with detailed Rich output

## Phase 5: Advanced Features

### 5.1 Better Model Support
- [ ] Add support for multiple LLM providers (OpenAI, Anthropic, etc.)
- [ ] Add model selection and switching
- [ ] Add model performance comparison
- [ ] Add custom prompt templates per model

### 5.2 Enhanced Filtering and Selection
- [ ] Add JQL query builder with Rich interface
- [ ] Add saved filter management
- [ ] Add ticket preview before processing
- [ ] Add batch processing with confirmation

### 5.3 Reporting and Export
- [ ] Add Rich-formatted reports
- [ ] Add export to various formats (JSON, CSV, HTML)
- [ ] Add processing history tracking
- [ ] Add audit trail generation

## Implementation Checklist

### Dependencies and Setup
- [x] Add `rich >= 13.0.0` to pyproject.toml
- [x] Add `typer >= 0.9.0` to pyproject.toml
- [x] Install dependencies: `poetry install`
- [x] Test basic imports and functionality

### Core Infrastructure
- [x] Create `src/jiraclean/ui/__init__.py`
- [x] Create `src/jiraclean/ui/console.py` (Rich console singleton)
- [x] Create `src/jiraclean/ui/components.py` (reusable Rich components)
- [x] Create `src/jiraclean/ui/formatters.py` (ticket formatting)
- [x] Create `src/jiraclean/cli/` module for Typer commands
- [x] Test UI component imports successfully

### CLI Implementation (Phase 1)
- [x] Create `src/jiraclean/cli/app.py` (main Typer app)
- [x] Create `src/jiraclean/cli/commands.py` (command implementations)
- [x] Create `src/jiraclean/cli/main.py` (entry point)
- [x] Implement main command with Rich formatting
- [x] Implement config subcommand
- [x] Implement setup subcommand
- [x] Test Typer CLI with Rich output
- [x] Verify beautiful formatted help and output
- [x] Add interactive elements and confirmation prompts
- [x] Implement Rich-formatted processing headers
- [x] Add comprehensive command-line options with validation

### Rich Output Implementation (Phase 2 Foundation)
- [x] Create Rich console singleton with custom theme
- [x] Implement TicketCard component for prominent ticket display
- [x] Create StatusIndicator for consistent status messaging
- [x] Build ProgressTracker for operation progress
- [x] Develop comprehensive formatters for all data types
- [x] Add mode banners (DRY RUN vs PRODUCTION)
- [x] Implement error formatting with Rich panels
- [x] Test Rich components with real Jira data

### Migration Strategy
- [x] Create new Typer-based CLI alongside existing argparse
- [x] Maintain backward compatibility during transition
- [ ] Gradually migrate functionality (bridge implemented)
- [ ] Add feature flags for new vs old interface
- [ ] Update documentation and examples

### Testing and Validation
- [x] Test with real Jira data (NEMS project)
- [x] Test both dry-run and production modes
- [x] Test error scenarios and edge cases
- [x] Validate output formatting across different terminal sizes
- [x] Test with different color schemes and accessibility

### Documentation Updates
- [x] Update README.md with new CLI examples
- [x] Update quickstart guide with Rich output examples
- [ ] Add screenshots/examples of new output format
- [x] Update contributing guide with UI development guidelines

## Success Criteria

### User Experience
- [ ] Original tickets are visually distinct and prominent
- [ ] LLM feedback is clearly differentiated from ticket data
- [ ] Progress is clearly communicated during processing
- [ ] Errors are helpful and actionable
- [ ] CLI is intuitive and self-documenting

### Technical Quality
- [ ] All existing functionality preserved
- [ ] Performance is maintained or improved
- [ ] Code is well-structured and maintainable
- [ ] Rich components are reusable and consistent
- [ ] Configuration is robust and user-friendly

### Visual Design
- [ ] Consistent color scheme and styling
- [ ] Good contrast and accessibility
- [ ] Responsive to different terminal sizes
- [ ] Professional and polished appearance
- [ ] Clear information hierarchy

## Timeline Estimate
- **Phase 1**: 2-3 days (CLI with Typer)
- **Phase 2**: 3-4 days (Rich output implementation)
- **Phase 3**: 2-3 days (Enhanced configuration)
- **Phase 4**: 2-3 days (Output formatting)
- **Phase 5**: 3-4 days (Advanced features)

**Total**: ~12-17 days for complete implementation

## Risk Mitigation
- Maintain backward compatibility throughout
- Implement feature flags for gradual rollout
- Extensive testing with real data
- Documentation updates parallel to development
- Regular user feedback collection

---

**Next Steps**: Please review and approve this development plan before proceeding with implementation.
