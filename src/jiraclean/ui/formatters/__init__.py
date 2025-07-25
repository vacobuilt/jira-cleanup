"""
UI formatters package.

This package contains formatter classes that handle the display of
analysis results in the user interface. Each analyzer type has its
own formatter that knows how to present results appropriately.
"""

from .base_formatter import BaseFormatter

__all__ = ['BaseFormatter']
