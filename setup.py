#!/usr/bin/env python3
"""Setup script for BatchRunner."""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

setup(
    name="batchrunner",
    version="1.0.0",
    author="ATLAS (Team Brain)",
    author_email="metaphy@example.com",
    description="Command Batch Orchestration Made Simple",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/DonkRonk17/BatchRunner",
    py_modules=["batchrunner"],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    entry_points={
        "console_scripts": [
            "batchrunner=batchrunner:main",
        ],
    },
    keywords="batch command runner orchestration automation cli",
    project_urls={
        "Bug Reports": "https://github.com/DonkRonk17/BatchRunner/issues",
        "Source": "https://github.com/DonkRonk17/BatchRunner",
    },
)
