from pymongo import MongoClient
from pymongo.server_api import ServerApi
import os

def get_database(is_local:bool = False):

    if is_local:
        # Provide the mongodb atlas url to connect python to mongodb using pymongo
        # CONNECTION_STRING = "mongodb+srv://user:pass@cluster.mongodb.net/myFirstDatabase"
        CONNECTION_STRING = "mongodb://localhost:27017"

        # Create a connection using MongoClient. You can import MongoClient or use pymongo.MongoClient
        client = MongoClient(CONNECTION_STRING)

        # Create the database for our example (we will use the same database throughout the tutorial
        return client['Arol']
    else:
        uri = os.getenv("MONGO_DB_URL")
        # Create a new client and connect to the server
        client = MongoClient(uri, server_api=ServerApi('1'))
        return client['ArolCluster']


# This is added so that many files can reuse the function get_database()
if __name__ == "__main__":
    # Get the database
    dbname = get_database(is_local=False)
