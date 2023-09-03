from setuptools import find_packages, setup

CLASSIFIERS = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3 :: Only",
    "Natural Language :: English",
]

KEYWORDS = ["python", "gofile", "api", "gofileio", "gofile.io"]

DEPENDENCIES = ["requests"]

DESCRIPTION = "A python library for communicating with the Gofile API."
with open("README.md", "r") as readme_file, open("CHANGELOG.md", "r") as changelog_file:
    LONG_DESCRIPTION = f"{readme_file.read()}\n\n{changelog_file.read()}"

setup(
    name="gofile-api",
    version="0.0.7",
    description="A python library for communicating with the Gofile API.",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    url="https://github.com/objectiveSquid/GoFile-API",
    author="Magnus Zahle",
    author_email="objectivesquid@outlook.com",
    license="MIT",
    classifiers=CLASSIFIERS,
    keywords=KEYWORDS,
    packages=find_packages(),
    install_requires=DEPENDENCIES,
)
