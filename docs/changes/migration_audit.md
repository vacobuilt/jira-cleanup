# Migration Audit Document

This document tracks the audit of parallel code structures and identifies critical differences and special handling needed during the migration.

## File Structure Comparison

| Flat Structure | Jiraclean Structure | Status | Notes |
|----------------|---------------------|--------|-------|
| src/main.py | src/jiraclean/main.py | Analyzed | Jiraclean version is more feature-rich, no merge needed |
| src/iterators/base.py | src/jiraclean/iterators/base.py | Analyzed | Jiraclean version has total_tickets removed (per design decision) |
| src/jirautil/interfaces.py | src/jiraclean/jirautil/interfaces.py | Migrated | Copied flat structure file to jiraclean |
| src/jirautil/exceptions.py | src/jiraclean/jirautil/exceptions.py | Merged | Combined documentation and content |
| src/jirautil/dry_run_client.py | src/jiraclean/jirautil/dry_run_client.py | Merged | Added factory function from flat version |
| src/jirautil/__init__.py | src/jiraclean/jirautil/__init__.py | Merged | Unified exports and documentation |
| src/utils/__init__.py | src/jiraclean/utils/__init__.py | Merged | Added exports from flat version |
| src/llm/__init__.py | src/jiraclean/llm/__init__.py | Merged | Improved documentation |
| src/processors/__init__.py | src/jiraclean/processors/__init__.py | Merged | Updated formatting and documentation |
| src/iterators/__init__.py | src/jiraclean/iterators/__init__.py | Merged | Improved documentation |
| src/jirautil/client.py | src/jiraclean/jirautil/client.py | To Compare | Jira client implementation |
| src/prompts/registry.py | src/jiraclean/prompts/registry.py | To Compare | Prompt registry implementation |
| src/iterators/project.py | src/jiraclean/iterators/project.py | To Compare | Project iterator implementation |
| src/llm/assessment.py | src/jiraclean/llm/assessment.py | To Compare | LLM assessment logic |
| src/processors/quiescent.py | src/jiraclean/processors/quiescent.py | To Compare | Quiescent processor implementation |
| src/domain/ | N/A | To Migrate | Domain layer (new architecture) |
| src/infrastructure/ | N/A | To Migrate | Infrastructure layer (new architecture) |

## Critical Differences to Address

Any critical differences found between the parallel implementations will be documented here.

## Import Pattern Changes

Document any import pattern updates that need to happen across the codebase.

## Domain & Infrastructure Integration

Notes on how to integrate the domain-driven architecture components.

## Baseline Functionality

Commands to run for baseline functionality testing:

```bash
# Basic functionality test
python -m jiraclean.main --project UHES --dry-run --max-tickets 2

# Expected outcome: 
# Should process 2 tickets from UHES project in dry run mode
```

## Special Cases

Document any special cases or custom implementations that need careful handling.

## Progress Tracking

- [ ] File comparison completed
- [ ] Critical differences documented
- [ ] Baseline functionality established
- [ ] Domain integration plan finalized
- [ ] Version control setup
