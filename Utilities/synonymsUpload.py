from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import json
import certifi


class synonymsUpload:
    def __init__(self, dbName):
        self.dbName = dbName

    def get_database(self):

        # Provide the mongodb atlas url to connect python to mongodb using pymongo
        CONNECTION_STRING = "mongodb+srv://otaku:Fet4pXs4FmBVUA6U@animetracker.672e6pq.mongodb.net/test"

        # Create a connection using MongoClient. You can import MongoClient or use pymongo.MongoClient
        cert = certifi.where()
        client = MongoClient(CONNECTION_STRING, tlsCAFile=cert)

        # check connection
        try:
            # The ismaster command is cheap and does not require auth.
            print("server info:\n\n", client.server_info(), "\n")
            print("\nConnection is Successful !!\n")

        except ConnectionFailure:
            print("Server not available")

        # Create the database for our example (we will use the same database throughout the tutorial
        return client[self.dbName]

    def extract_synonyms(self, file_path):
        synonymCollection = []

        with open(file_path, 'r') as anime_file:
            data = json.load(anime_file)

            for anime in data:
                collectionItem = {
                    'mappingType': 'equivalent',
                    'synonyms': [anime['title']] + anime['synonyms']
                }

                synonymCollection.append(collectionItem)

        return synonymCollection

    def add_to_collection(self, collection, items):
        collection.insert_many(items)
