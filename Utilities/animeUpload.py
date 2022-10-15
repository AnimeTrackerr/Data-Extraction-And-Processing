from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import json
import certifi
import os
import re


class animeUpload:
    def __init__(self, dbName):
        self.dbName = dbName

    def connect_database(self, URI):

        # Provide the mongodb atlas url to connect python to mongodb using pymongo
        CONNECTION_STRING = URI

        # Create a connection using MongoClient. You can import MongoClient or use pymongo.MongoClient
        cert = certifi.where()
        client = MongoClient(CONNECTION_STRING, tlsCAFile=cert)

        # check connection
        try:
            print("server info:\n\n", client.server_info(), "\n")
            print("\nConnection is Successful !!\n")

        except ConnectionFailure:
            print("Server not available")

        # Create or get the database
        return client[self.dbName]

    def extract_anime(self, work_dir, batch_no=0):
        animeCollection = []
        files = []
        pat = '(animedata\()([0-9]+)(-[0-9]+)(\).json)'
        dir = f'{work_dir}\\CombinedAnimeData'

        # sort files
        for file in os.listdir(dir):
            files.append((file, int(re.match(pat, file).groups()[1])))

        files = [file_name[0]
                 for file_name in sorted(files, key=lambda k: k[1])[batch_no:]]

        # get anime data
        for file in files:
            with open(f'{dir}\\{file}', 'r') as anime_file:

                data = json.load(anime_file)

                for anime in data:
                    animeCollection.append(anime)

        # return animeCollection
        return animeCollection

    def add_to_collection(self, collection, items):
        collection.insert_many(items)
