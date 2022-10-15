import json
import requests as req


class DataScrapper:
    def __init__(self, url, download_location):
        self.url = url
        self.download_location = download_location

    def extract_anime_data(self):
        res = req.get(self.url).text
        return json.loads(res)["data"]

    def save_data(self, data):
        with open(f'{self.download_location}/anime_data.json', 'w', encoding='utf-8') as file:
            json.dump(data, file)
