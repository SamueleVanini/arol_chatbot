import os
from dotenv import load_dotenv

load_dotenv() # This loads all variables from .env automatically

REDIS_URL: str = os.getenv('REDIS_URL')
MONGO_DB_URL: str = os.getenv("MONGO_DB_URL")
USE_DOCKER = bool(int(os.getenv("USE_DOCKER", "0")))  # Use "0" or "1" in .env
