# Package Structure Consolidation Plan

## Current State Analysis

Our codebase currently has parallel package structures and configuration mismatches that need to be resolved:

1. **Parallel Package Structures**:
   - Flat structure at `src/` root level (main.py, iterators/, jirautil/, etc.)
   - Namespaced structure under `src/jiraclean/` (main.py, iterators/, jirautil/, etc.)

2. **Package Configuration Mismatch**:
   - `pyproject.toml` (Poetry): Defines package as "jira-cleanup" with `packages = [{include = "jiraclean", from = "src"}]`
   - `setup.py`: Defines package as "jira_cleanup" with `find_packages(where="src")`
   - Entry points are different: `jiraclean.main:main` vs `src.main:main`

3. **Domain-Driven Architecture**:
   - `src/domain/` and `src/infrastructure/` directories not currently integrated 
   - Appears to represent a future architecture direction

## Migration Goal

Consolidate all functionality under the `jiraclean` namespace for cleaner architecture, simplified imports, and consistent package configuration. Remove redundant files and configurations.

## Migration Plan

### Phase 1: Audit & Preparation

1. **File Comparison**:
   - Compare all files between old (flat) and new (jiraclean) structure
   - Identify any unique code or modifications in either version
   - Document any critical differences for special handling

2. **Baseline Functionality**:
   - Run the application in its current state to ensure it works
   - Document the command used and expected output
   - Create a baseline for post-migration validation

3. **Domain Integration Planning**:
   - Evaluate how `domain/` and `infrastructure/` directories should be integrated
   - Determine if they should be moved under jiraclean or kept separate
   - Plan appropriate import patterns for integration

4. **Version Control**:
   - Create a new git branch for the migration
   - Commit current state as baseline
   - Consider tagging the pre-migration state for reference

### Phase 2: Package Configuration

1. **Standard Configuration**:
   - Remove `setup.py` since we're using Poetry via `pyproject.toml`
   - Verify that `pyproject.toml` correctly references `jiraclean.main:main` as entry point
   - Ensure all dependencies are correctly specified in `pyproject.toml`

2. **Build Validation**:
   - Verify package can be built with Poetry: `poetry build`
   - Check that the built package has the correct structure
   - Validate that no files are missing from the distribution

### Phase 3: Code Migration

1. **Module by Module Migration**:
   - Systematically work through each module in the flat structure
   - For each module, determine if there's already an equivalent in jiraclean
   - Merge any unique code or functionality
   - Prioritize order: utils → models → core functionality → CLI

2. **Import Updates**:
   - Update all imports in migrated files to use `jiraclean` namespace
   - Search for all relative imports and update accordingly
   - Example: change `from utils.config import X` to `from jiraclean.utils.config import X`

3. **Domain Integration**:
   - Move `domain/` and `infrastructure/` under the `jiraclean` namespace
   - Update imports in these modules to reflect new location
   - Ensure any references to these modules are updated throughout codebase

4. **Special Cases**:
   - Handle any custom modifications or unique functionality identified in the audit
   - Pay special attention to:
     - Configuration loading
     - File paths resolution
     - Plugin/extension mechanisms

### Phase 4: Validation & Cleanup

1. **Functional Testing**:
   - Run the application with the exact commands documented in Phase 1
   - Verify all functionality works as expected
   - Test with various command-line options

2. **Redundant File Removal**:
   - Once functionality is confirmed, remove redundant files:
     - `src/main.py`
     - `src/iterators/`, `src/jirautil/`, `src/llm/`, etc.
     - `src/utils/`, `src/processors/`, `src/prompts/`
   - Be careful to only remove files that have been successfully migrated

3. **Installation Testing**:
   - Install the package locally with Poetry: `poetry install`
   - Verify the CLI entry point works: `jiraclean --help`
   - Test core functionality from the installed package

4. **Final Cleanup**:
   - Remove any temporary files or backups
   - Remove any debugging code or comments
   - Ensure consistent code style across all files

### Phase 5: Documentation

1. **README Updates**:
   - Update installation instructions
   - Update usage examples with correct import patterns
   - Ensure CLI examples use the correct command names

2. **Architecture Documentation**:
   - Document the consolidated package structure
   - Update any architecture diagrams
   - Document the rationale for the consolidation in `design_decisions.md`

3. **Code Examples**:
   - Update any example code in documentation
   - Verify examples match the current implementation

## Verification Checklist

After completing all phases, verify:

- [ ] All functionality continues to work as before
- [ ] Package builds successfully with Poetry
- [ ] CLI entry point works correctly
- [ ] All tests pass
- [ ] No duplicate or redundant files remain
- [ ] Documentation accurately reflects the new structure
- [ ] Code imports are consistent throughout the codebase

## Rollback Plan

In case of issues:

1. Return to the tagged/branched version from Phase 1
2. Document specific issues encountered
3. Create a more targeted migration plan addressing the issues

## Timeline

Estimated timeline for completion:

- Phase 1 (Audit & Preparation): 1 day
- Phase 2 (Package Configuration): 0.5 day
- Phase 3 (Code Migration): 2-3 days
- Phase 4 (Validation & Cleanup): 1 day
- Phase 5 (Documentation): 0.5 day

Total estimated time: 5-6 days of effort
