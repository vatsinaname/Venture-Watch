from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="startup-agent",
    version="0.1.0",
    author="Rishabh Vats",
    author_email="your.email@example.com",
    description="AI agent that finds funded startups matching your skills",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/vatsinaname/Venture-Watch",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.31.0",
        "python-dotenv>=1.0.0",
        "langchain>=0.0.292",
        "langchain-openai>=0.0.2",
        "pydantic>=2.4.2",
        "fastapi>=0.104.1",
        "uvicorn>=0.23.2",
        "jinja2>=3.1.2",
        "tenacity>=8.2.3",
        "python-dateutil>=2.8.2",
        "schedule>=1.2.0",
        "reportlab>=4.0.4",
        "streamlit>=1.27.2",
        "markdown>=3.4.4",
        "plotly>=5.18.0",
        "pandas>=2.0.0",
    ],
    entry_points={
        "console_scripts": [
            "startup-agent=startup_agent.run:main",
        ],
    },
) 