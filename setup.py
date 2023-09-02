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
with open("CHANGELOG.txt", "r") as changelog, open("README.txt", "r") as readme:
    LONG_DESCRIPTION = """Description
-------------------
A python library for communicating with the Gofile API.

Features
-------------------
Get an available server.
Upload a file, to a directory, or to the root folder.
Create a guest account.
Get contents of a folder.
Create a folder.
Get the account information.
Set option for a content id.

Changelog
==========

0.0.1 (02. of september 2023)
-------------------
First upload

0.0.2 (02. of september 2023)
-------------------
Added more documentation

0.0.3 (02. of september 2023)
-------------------
Fixed long description on PyPi

0.0.4 (02. of september 2023)
-------------------
Fixed long description on PyPi, again
Added documentation for all functions, and improved existing documentation
Fixed GoFileSession.upload_file"""

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
