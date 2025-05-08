# Migration Tools

This directory contains utilities to help with the migration of the jira-cleanup package structure from a flat structure to a namespaced structure under `jiraclean`.

## Available Tools

### compare_structures.py

This script analyzes the differences between the parallel package structures in the codebase and generates a detailed migration report.

#### Usage

```bash
# Run directly
python migration_tools/compare_structures.py

# Make executable first
chmod +x migration_tools/compare_structures.py
./migration_tools/compare_structures.py
```

#### What it Does

1. Analyzes all files in both the flat and jiraclean structures
2. Categorizes files as:
   - Identical (same content in both structures)
   - Similar (different content)
   - Flat only (needs migration)
   - Jiraclean only

3. Generates a detailed migration report (`migration_report.md`) with:
   - Summary statistics
   - Lists of files requiring attention
   - Migration recommendations

4. Prioritizes files based on similarity score to help identify which files need the most attention

#### Configuration

By default, the script is configured to:
- Exclude `domain/`, `infrastructure/`, and `__pycache__/` directories from comparison
- Include `.py`, `.md`, `.yaml`, `.yml`, and `.txt` files
- Examine files in `src/` and `src/jiraclean/`

## Migration Process

The general migration workflow is:

1. Run `compare_structures.py` to generate the migration report
2. Review the report and plan your migration
3. Start with merging files that have the lowest similarity scores
4. Move unique files from the flat structure to the jiraclean namespace
5. Update imports in all files to use the jiraclean namespace
6. Test the consolidated structure
7. Remove redundant files from the flat structure
