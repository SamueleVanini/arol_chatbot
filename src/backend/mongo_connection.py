from pymongo import MongoClient
from pymongo.server_api import ServerApi
from src.core.config import MONGO_DB_URL, USE_DOCKER


def get_database():
    # Provide the mongodb atlas url to connect python to mongodb using pymongo OR local db
    uri = MONGO_DB_URL
    if not uri:
        raise ValueError("MONGO_DB_URL environment variable is not set.")

    if USE_DOCKER:
        print("Connecting Mongo image on Docker ...")
        client = MongoClient(uri)
    else:
        print("Connection to MongoDB ATLAS Server ...")
        client = MongoClient(uri, server_api=ServerApi('1'))

    return client["ArolCluster"]


# This is added so that many files can reuse the function get_database()
if __name__ == "__main__":
    # Get the database
    dbname = get_database()
