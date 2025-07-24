#!/usr/bin/env python3
"""
Entry point for running jiraclean as a module.

This allows the package to be executed with:
    python -m jiraclean
"""

from jiraclean.main import main

if __name__ == "__main__":
    exit(main())
