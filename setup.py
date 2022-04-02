import setuptools


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


setuptools.setup(
    name="MLBPlayerIDs",
    version="0.0.1",
    author="Jacob Lee",
    author_email="JLpython@outlook.com",

    description="A package for scraping IDs for MLB players",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/JLpython-py/MLBPlayerIDs",
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],

    packages=setuptools.find_packages(
        exclude=["mlbides.tests"]
    ),
    include_package_data=True,
    package_data={"": ["data/*.json"]},

    python_requires=">=3.8",
)
