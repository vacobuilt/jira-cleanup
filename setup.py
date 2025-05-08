#!/usr/bin/env python3
"""
Setup script for Jira Cleanup package.
"""

from setuptools import setup, find_packages

setup(
    name="jira_cleanup",
    version="0.1.0",
    description="A configurable, policy-based tool for automated Jira ticket governance",
    author="Trilliant",
    author_email="info@trilliant.io",
    packages=find_packages(),
    install_requires=[
        "jira>=3.5.0",
        "pyyaml>=6.0",
        "python-dotenv>=1.0.0",
        "requests>=2.31.0",
        "typing-extensions>=4.7.0",
    ],
    entry_points={
        "console_scripts": [
            "jira-cleanup=jira_cleanup.src.main:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
    python_requires=">=3.11",
)
