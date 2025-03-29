from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ai-pr-reviewer",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="An AI-powered Pull Request reviewer using OpenAI GPT",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/pr_reviewer",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Quality Assurance",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.11",
    install_requires=[
        "openai>=1.69.0",
        "PyGithub>=2.1.1",
        "pydantic>=2.10.6",
        "aiohttp>=3.11.4",
    ],
    entry_points={
        'console_scripts': [
            'pr-reviewer=src.run_reviewer:main',
        ],
    },
) 