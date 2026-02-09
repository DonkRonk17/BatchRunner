#!/usr/bin/env python3
"""
BatchRunner - Parallel command executor with dependency management

Setup script for pip installation.
"""

from pathlib import Path
from setuptools import setup, find_packages

# Read README for long description
readme_file = Path(__file__).parent / "README.md"
long_description = ""
if readme_file.exists():
    long_description = readme_file.read_text(encoding='utf-8')

setup(
    name="batchrunner",
    version="1.0.0",
    author="ATLAS (Team Brain)",
    author_email="logan@metaphy.com",
    description="Parallel command executor with dependency management",
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
    keywords="command executor batch parallel dependency automation ci-cd",
    project_urls={
        "Bug Reports": "https://github.com/DonkRonk17/BatchRunner/issues",
        "Source": "https://github.com/DonkRonk17/BatchRunner",
        "Documentation": "https://github.com/DonkRonk17/BatchRunner#readme",
    },
)
