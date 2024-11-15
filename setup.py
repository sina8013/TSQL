from setuptools import setup, find_packages

setup(
    name="tsqlite",
    version="0.1.1",
    author="Sina Saeedi",
    author_email="sina8013@gmail.com",
    description="A Python library for managing and syncing SQLite databases over Telegram channels with secure encryption.",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/sina8013/TSQL",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries",
        "Topic :: Database :: Database Engines/Servers",
        "Topic :: Communications :: Chat",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "telethon>=1.24.0",
        "pycryptodome>=3.15.0",
        "pandas>=1.3.0",
    ],
)
