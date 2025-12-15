"""Setup script for socionics-research package."""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text(encoding="utf-8")

# Read requirements
requirements_path = Path(__file__).parent / "requirements.txt"
requirements = [
    line.strip()
    for line in requirements_path.read_text(encoding="utf-8").splitlines()
    if line.strip() and not line.startswith("#")
]

setup(
    name="socionics-research",
    version="0.1.0",
    description="Research platform for socionics personality analysis with ML/AI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="socionics-research contributors",
    url="https://github.com/jmbvcxd/socionics-research",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=requirements,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
)
