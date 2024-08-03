# Introduction

# Development

### Local environment
1. Create an environment using the built-in tool ```venv``` or the module ```virtualenv``` (all the instruction will consider only venv)
  ```
  python -m venv venv
  source venv/bin/activate   # on macOs/Linux
  venv\Scripts\activate.bat  # on Windows
  pip install -r requirements.txt
  ```
2. Create the dataset from the pdf catalogon running:
  ```
  python src/preprocessing/pdf_extraction.py
  ```

### Testing
To run all the test go to the project's root directory and run ```python -m unittest discover```.