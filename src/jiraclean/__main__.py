#!/usr/bin/env python3
"""
Entry point for running jiraclean as a module.

This allows the package to be executed with:
    python -m jiraclean

Now uses the new Typer CLI instead of the old argparse interface.
"""

from jiraclean.cli.main import main

if __name__ == "__main__":
    main()
