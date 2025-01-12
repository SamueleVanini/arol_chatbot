import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()  # This loads all variables from .env automatically

REDIS_URL: str = os.getenv("REDIS_URL")
MONGO_DB_URL: str = os.getenv("MONGO_DB_URL")
USE_DOCKER = bool(int(os.getenv("USE_DOCKER", "0")))  # Use "0" or "1" in .env


def configure_system():
    """Entry point to configure the running system, add in the body of the function all the logic to configure the chatbot"""
    load_dotenv()


# file data path
JSON_MACHINES_FILE_PATH = "./data/processed_catalog.json"
MACHINE_PARAGRAPH = Path("./data/json_rewritten.csv")
COMPANY_INFO_FILE_PATH = "./data/company_info_cleaned.txt"
COMPANY_INFO_2_FILE_PATH = "./data/company_info_cleaned_v2.txt"

# collections info
PERSIST_DIRECTORY = "./data"
SELF_QUERYING_COLLECTION_NAME = "self_querying_collection"
PARRENT_DOCUMENT_COLLECTION = "parrent_document_collection"
COMPANY_INFO_COLLECTION = "company_info_collection"
