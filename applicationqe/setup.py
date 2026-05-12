#!/usr/bin/env python
"""Setup file for ui-automation-framework package."""

from setuptools import setup, find_packages

setup(
    packages=find_packages(
        include=[
            "config",
            "config.*",
            "pages",
            "pages.*",
            "utils",
            "utils.*",
            "tests",
            "tests.*",
            "fixtures",
            "fixtures.*",
        ]
    ),
)
