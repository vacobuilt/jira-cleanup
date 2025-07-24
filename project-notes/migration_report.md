# Migration Comparison Report

## Summary

- Identical files: 7
- Similar files (need merging): 14
- Files only in flat structure (need migration): 1
- Files only in jiraclean structure: 2

## Files Needing Merge (Different Content)

| File Path | Similarity | Flat Path | Jiraclean Path |
|-----------|------------|-----------|----------------|
| jirautil/__init__.py | 0.15 | /Users/ldawson/repos/jira_cleanup/src/jirautil/__init__.py | /Users/ldawson/repos/jira_cleanup/src/jiraclean/jirautil/__init__.py |
| utils/__init__.py | 0.29 | /Users/ldawson/repos/jira_cleanup/src/utils/__init__.py | /Users/ldawson/repos/jira_cleanup/src/jiraclean/utils/__init__.py |
| llm/__init__.py | 0.38 | /Users/ldawson/repos/jira_cleanup/src/llm/__init__.py | /Users/ldawson/repos/jira_cleanup/src/jiraclean/llm/__init__.py |
| processors/__init__.py | 0.40 | /Users/ldawson/repos/jira_cleanup/src/processors/__init__.py | /Users/ldawson/repos/jira_cleanup/src/jiraclean/processors/__init__.py |
| iterators/__init__.py | 0.48 | /Users/ldawson/repos/jira_cleanup/src/iterators/__init__.py | /Users/ldawson/repos/jira_cleanup/src/jiraclean/iterators/__init__.py |
| jirautil/exceptions.py | 0.62 | /Users/ldawson/repos/jira_cleanup/src/jirautil/exceptions.py | /Users/ldawson/repos/jira_cleanup/src/jiraclean/jirautil/exceptions.py |
| jirautil/dry_run_client.py | 0.77 | /Users/ldawson/repos/jira_cleanup/src/jirautil/dry_run_client.py | /Users/ldawson/repos/jira_cleanup/src/jiraclean/jirautil/dry_run_client.py |
| iterators/base.py | 0.78 | /Users/ldawson/repos/jira_cleanup/src/iterators/base.py | /Users/ldawson/repos/jira_cleanup/src/jiraclean/iterators/base.py |
| main.py | 0.79 | /Users/ldawson/repos/jira_cleanup/src/main.py | /Users/ldawson/repos/jira_cleanup/src/jiraclean/main.py |
| prompts/registry.py | 0.87 | /Users/ldawson/repos/jira_cleanup/src/prompts/registry.py | /Users/ldawson/repos/jira_cleanup/src/jiraclean/prompts/registry.py |
| iterators/project.py | 0.91 | /Users/ldawson/repos/jira_cleanup/src/iterators/project.py | /Users/ldawson/repos/jira_cleanup/src/jiraclean/iterators/project.py |
| llm/assessment.py | 0.94 | /Users/ldawson/repos/jira_cleanup/src/llm/assessment.py | /Users/ldawson/repos/jira_cleanup/src/jiraclean/llm/assessment.py |
| processors/quiescent.py | 0.97 | /Users/ldawson/repos/jira_cleanup/src/processors/quiescent.py | /Users/ldawson/repos/jira_cleanup/src/jiraclean/processors/quiescent.py |
| jirautil/client.py | 1.00 | /Users/ldawson/repos/jira_cleanup/src/jirautil/client.py | /Users/ldawson/repos/jira_cleanup/src/jiraclean/jirautil/client.py |

## Files To Migrate (Flat Structure Only)

| File Path | Current Location | Target Location |
|-----------|------------------|----------------|
| jirautil/interfaces.py | /Users/ldawson/repos/jira_cleanup/src/jirautil/interfaces.py | src/jiraclean/jirautil/interfaces.py |

## Identical Files (Can Be Removed After Verification)

| File Path | Flat Path | Jiraclean Path |
|-----------|-----------|----------------|
| __init__.py | /Users/ldawson/repos/jira_cleanup/src/__init__.py | /Users/ldawson/repos/jira_cleanup/src/jiraclean/__init__.py |
| processors/base.py | /Users/ldawson/repos/jira_cleanup/src/processors/base.py | /Users/ldawson/repos/jira_cleanup/src/jiraclean/processors/base.py |
| prompts/__init__.py | /Users/ldawson/repos/jira_cleanup/src/prompts/__init__.py | /Users/ldawson/repos/jira_cleanup/src/jiraclean/prompts/__init__.py |
| prompts/templates/closure_recommendation.yaml | /Users/ldawson/repos/jira_cleanup/src/prompts/templates/closure_recommendation.yaml | /Users/ldawson/repos/jira_cleanup/src/jiraclean/prompts/templates/closure_recommendation.yaml |
| prompts/templates/quiescent_assessment.yaml | /Users/ldawson/repos/jira_cleanup/src/prompts/templates/quiescent_assessment.yaml | /Users/ldawson/repos/jira_cleanup/src/jiraclean/prompts/templates/quiescent_assessment.yaml |
| utils/config.py | /Users/ldawson/repos/jira_cleanup/src/utils/config.py | /Users/ldawson/repos/jira_cleanup/src/jiraclean/utils/config.py |
| utils/formatters.py | /Users/ldawson/repos/jira_cleanup/src/utils/formatters.py | /Users/ldawson/repos/jira_cleanup/src/jiraclean/utils/formatters.py |

## Next Steps

1. Start with merging similar files, beginning with those having lowest similarity score
2. Migrate files that only exist in the flat structure to the jiraclean namespace
3. Update imports in all files to use the jiraclean namespace
4. After testing the consolidated structure, remove redundant files from the flat structure
