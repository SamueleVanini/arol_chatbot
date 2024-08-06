# Introduction

# Development

## Local environment
All the development have been done assuming a python version greater or equal than 3.12, previous versions are not tested or directly supported.
The following steps will guide you on the local development set-up.

1. Create a virtual environment using the built-in tool ```venv``` or the module ```virtualenv``` (all the instruction will consider only venv)
    ```
    python -m venv venv
    source venv/bin/activate   # on macOs/Linux
    venv\Scripts\activate.bat  # on Windows
    pip install -r requirements.txt
    ```
2. Install the project as local module to use the CLI utility (important: before running the following command be sure be inside the virtual environment, otherwise the project will be installed globally)
    ```
    pip install -e . # run it from the same directory of pyproject.toml
    ```
3. Now the CLI tool for parsing the pdf catalog is available using the command ```arol-preprocessing```. Description of the options and configurations available for the tool are avaible using the command ```arol-preprocessing -h``` or ```arol-preprocessing --help```.

## Testing
To run all the available tests, navigate to the project's root directory and run ```python -m unittest discover```. For all other options on test run refer to the documentation/guides in [PROJECT.md](PROJECT.md).

## Libraries used and useful guides
Refer to [PROJECT.md](PROJECT.md) for a list of all libraries, documentation and guides used to set-up and develop the project.