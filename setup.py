from setuptools import find_packages, setup

CLASSIFIERS = [
    "Development Status :: 5 - Production/Stable",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3 :: Only",
    "Natural Language :: English",
]

KEYWORDS = ["python", "gofile", "api", "gofileio", "gofile.io"]

DEPENDENCIES = ["requests"]

DESCRIPTION = "A python library for communicating with the Gofile API."
LONG_DESCRIPTION = """--------------------GoFile API--------------------

Description:

A python library for communicating with the Gofile API.

Features:

Get an available server.
Upload a file, to a directory, or to the root folder.
Create a guest account.
Get contents of a folder.
Create a folder.
Get the account information.
Set option for a content id."""

setup(
    name="gofile-api",
    version="0.0.4",
    description="A python library for communicating with the Gofile API.",
    long_description=LONG_DESCRIPTION,
    url="https://github.com/objectiveSquid/GoFile-API",
    author="Magnus Zahle",
    author_email="objectivesquid@outlook.com",
    license="MIT",
    classifiers=CLASSIFIERS,
    keywords=KEYWORDS,
    packages=find_packages(),
    install_requires=DEPENDENCIES,
)
