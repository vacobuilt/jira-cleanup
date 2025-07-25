# CLI Migration Checklist - Clean Typer Migration

**Goal**: Replace the old argparse CLI with the new Typer CLI completely, applying DRY and KISS principles.

**Status**: 🚀 **In Progress** - Clean migration without bridges or feature flags

---

## Phase 1: Core Migration (Remove Old CLI)

### 1.1 Analyze Current State
- [x] ✅ **Identify business logic in old main.py** - Located core processing functions
- [x] ✅ **Map Typer CLI structure** - Commands already created in `src/jiraclean/cli/`
- [x] ✅ **Identify entry points** - `pyproject.toml` and `__main__.py` need updates

### 1.2 Extract Business Logic
- [x] ✅ **Extract core functions from `src/jiraclean/main.py`** - Created `src/jiraclean/core/processor.py` with Rich integration
- [x] ✅ **Move ticket processing logic to Typer commands** - Integrated with `src/jiraclean/cli/commands.py`
- [x] ✅ **Update configuration handling** - Typer commands use existing config system with validation
- [x] ✅ **Preserve all functionality** - All features preserved with enhanced Rich output

### 1.3 Update Entry Points
- [x] ✅ **Update `src/jiraclean/__main__.py`** - Now points to Typer CLI
- [ ] ⏳ **Update `pyproject.toml` console scripts** - Ensure `jiraclean` command uses new CLI
- [x] ✅ **Remove old CLI imports** - Entry point now uses Typer CLI

---

## Phase 2: Rich Integration (Beautiful Output)

### 2.1 Replace Print Statements
- [ ] ⏳ **Update processors with Rich output** - Replace prints in `processors/quiescent.py`
- [ ] ⏳ **Update iterators with Rich progress** - Add progress bars in `iterators/project.py`
- [ ] ⏳ **Update main processing loop** - Use `TicketCard.create()` for ticket display
- [ ] ⏳ **Update error handling** - Use `format_error()` for all exceptions

### 2.2 Add Progress Indicators
- [ ] ⏳ **Jira API calls progress** - Add spinners for API requests
- [ ] ⏳ **LLM processing progress** - Show progress during assessment
- [ ] ⏳ **Ticket processing progress** - Overall progress bar for batch processing
- [ ] ⏳ **Status indicators** - Use `StatusIndicator` for operation feedback

### 2.3 Enhanced Display
- [ ] ⏳ **Ticket cards for each ticket** - Prominent display with `TicketCard.create()`
- [ ] ⏳ **Assessment formatting** - Rich panels for LLM feedback
- [ ] ⏳ **Summary tables** - Rich tables for final statistics
- [ ] ⏳ **Mode banners** - Clear DRY RUN vs PRODUCTION indicators

---

## Phase 3: Code Cleanup (DRY/KISS)

### 3.1 Remove Duplicate Code
- [ ] ⏳ **Remove old argparse logic** - Delete argument parsing from `main.py`
- [ ] ⏳ **Consolidate configuration parsing** - Single config system
- [ ] ⏳ **Remove duplicate imports** - Clean up unused imports
- [ ] ⏳ **Remove old CLI tests** - Keep only Typer CLI tests

### 3.2 Simplify Structure
- [ ] ⏳ **Single entry point** - Only Typer CLI accessible
- [ ] ⏳ **Clean function signatures** - Remove argparse-specific parameters
- [ ] ⏳ **Consolidate error handling** - Single error handling approach with Rich
- [ ] ⏳ **Remove unused functions** - Delete functions only used by old CLI

### 3.3 Update Documentation
- [ ] ⏳ **Update README examples** - Only show Typer CLI usage
- [ ] ⏳ **Update quickstart guide** - Remove old CLI references
- [ ] ⏳ **Update contributing guide** - Reflect new CLI structure
- [ ] ⏳ **Update help text** - Ensure all help is comprehensive

---

## Phase 4: Validation & Polish

### 4.1 Functionality Testing
- [ ] ⏳ **Test all commands work** - Verify main-command, config, setup
- [ ] ⏳ **Test with real Jira data** - Ensure processing works end-to-end
- [ ] ⏳ **Test error scenarios** - Verify Rich error handling
- [ ] ⏳ **Test different terminal sizes** - Ensure responsive design

### 4.2 Performance Validation
- [ ] ⏳ **Benchmark processing speed** - Ensure Rich doesn't slow down operations
- [ ] ⏳ **Memory usage check** - Verify no memory leaks with Rich components
- [ ] ⏳ **Startup time** - Ensure CLI starts quickly

### 4.3 Final Polish
- [ ] ⏳ **Create visual examples** - Screenshots of Rich output for documentation
- [ ] ⏳ **Update installation instructions** - Reflect single CLI approach
- [ ] ⏳ **Clean up test files** - Remove old CLI test files
- [ ] ⏳ **Final code review** - Ensure DRY/KISS principles applied throughout

---

## Files to Modify

### Primary Changes
- `src/jiraclean/cli/commands.py` - **Move real business logic here**
- `src/jiraclean/main.py` - **Extract reusable functions, remove CLI logic**
- `src/jiraclean/__main__.py` - **Point to Typer CLI**
- `src/jiraclean/processors/quiescent.py` - **Add Rich output**
- `src/jiraclean/iterators/project.py` - **Add Rich progress indicators**
- `pyproject.toml` - **Update console scripts**

### Files to Clean Up
- Remove argparse-specific code from `main.py`
- Remove old CLI test files
- Clean up unused imports throughout codebase

---

## Success Criteria

- ✅ **Single CLI Interface**: Only Typer CLI accessible to users
- ✅ **All Functionality Preserved**: No features lost in migration
- ✅ **Beautiful Rich Output**: All output uses Rich formatting
- ✅ **DRY Principles**: No duplicate code or logic
- ✅ **KISS Principles**: Simple, clean, maintainable code
- ✅ **Performance Maintained**: No regression in processing speed
- ✅ **Comprehensive Testing**: All functionality tested and working

---

**Last Updated**: 2025-07-24 18:58  
**Current Phase**: Phase 1 - Core Migration  
**Next Action**: Extract business logic from old main.py
