# Introduction

CapMate, a chatbot tailored for Arol Closure Systems. Developed as experimental project during the course System and Device Programming 2023-2024 at Politecnico of Torino, the repository contains all the code, data (e.g. pdf from which the data are extracted, ready to use data and dataset created for evaluation) and instruction to modify and launch the chatbot.

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
3. Now the CLI tool for parsing the pdf catalog and to load datasets is available using the command ```arol-preprocessing```. Description of the options and configurations available for the tool are available using the command ```arol-preprocessing -h``` or ```arol-preprocessing --help```.

## Environment variables needed for the project
You can find the requiring variables in `.env.example` file.
these are also the variables listed in the mentioned file:
```
LANGCHAIN_TRACING_V2=true

LANGCHAIN_API_KEY=Your_Api_Key_from_langSmith

GROQ_API_KEY=Your_Api_Key_from_GROQ

MONGO_DB_URL=mongodb+srv://{username}:{password}@{url_to_online_mongo_client} OR mongodb://mongodb:27017 (For Docker)

REDIS_URL=redis://username:password@Redis_URL:PORT OR redis://redis:6379 (For Docker)

USE_DOCKER= 0 OR 1
```

## Paths configuration
At run-time some paths are required by the chatbot (e.g.)

## Start Backend Server + Client

### 1. Run the project with Docker-Compose (Recommended)
Inorder to Run the project correctly you need to create `.env.docker` file in the `Root directory` of the project (where you find `Docker-compose.yaml` file).
put required keys as it is shown in the `.env.example` file. when you want to run the project with docker-compose, always put these fields as followings:
```
MONGO_DB_URL=mongodb://mongodb:27017/ArolCluster

REDIS_URL=redis://redis:6379

USE_DOCKER=1
```
Finally, to run the project run  `docker-compose up -d` in the `Root directory` of the project.

### 2. Run the project manually
You can run the Backend Server with `FastAPI` manually. For that make sure all the requirements are installed, then run the command `fastapi run .\src\backend\main.py` in the `Root` directory.
keep in mind that you need to create `.env` file with the mentioned keys in the `.env.example` file.
To start the Client part, inside the `client` directory run:
```
npm install
npm run dev
```
Important note: with the manual startup you need Redis and mongoDB atlas online client or use respecting docker images manually. Also, you should change `BASE_URL` in `API.JS` file.

## Testing
To run all the available tests, navigate to the project's root directory and run ```python -m unittest discover```. For all other options on test run refer to the documentation/guides in [Unit Test](https://docs.python.org/3/library/unittest.html).

# Evaluation pipeline

## Dataset
There are two different versions of the created dataset:
- full dataset can be found in `data/dataset.csv` 
- reduced version in `data/full_chain_dataset.csv`.

This distinction is done to the limitation of maximum number of tokens given by the free tier of the LLM provider Groq.
Both dataset are in csv format. The utility `arol-preprocesing dataset` by default skip the first line and any line that start with the character "#" (used inside the file to subdivide the data in thematic areas).

## Evaluation script
The solution provide two scripts to evaluate both the retriever and the full chain. To use them be sure to activate the virtual environment and to have uploaded the required dataset in Langsmith.
Move to the root folder of the project and run the command:
``` bash
python src/experiments/retriever_eval.py # for the retrieval evaluation
python src/experiments/full_chain_test.py # for the full chain evaluation
```
NOTES:
- `retriever_eval.py` suppose to find a dataset on Langsmith called "retrival_matches". If the dataset created has a different name change the value of the variable `DATASET_NAME`.
- `full_chain_matches.py` suppose to find a dataset on Langsmith called "retrival_matches". If the dataset created has a different name change the value of the variable `DATASET_NAME`.