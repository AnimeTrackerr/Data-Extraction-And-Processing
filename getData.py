import requests as req
import os
import re
import time
import math
import json
from dotenv import load_dotenv, find_dotenv
from Utilities.Directory import Directory
from Utilities.animeUpload import animeUpload
from Scrapper.DataScrapper import DataScrapper
from Scrapper.MALDataScrapper import MALDataScrapper


if __name__ == "__main__":
    # Step 0: define/load variables
    check_expiry_before = 1*24*3600  # format = days * hrs/day * seconds/hr
    load_dotenv(find_dotenv())
    time_zone = os.getenv('T_ZONE')

    # Step 1: create all the necessary directories and files (NEEDED)
    createDirsObj = Directory(work_dir=os.getcwd())
    createDirsObj.createDirs(
        'RawData', 'CombinedAnimeData', 'ParamsAndHeaders', 'LogFiles')

    # Step 2: get, process and save data (OPTIONAL, IF NEEDED)
    # data_scrapper = DataScrapper(url="https://raw.githubusercontent.com/manami-project/anime-offline-database/master/anime-offline-database.json",download_location=f'os.getcwd()\\RawData')
    # data = data_scrapper.extract_anime_data()
    # data_scrapper.save_data(data)

    # Step 3: scrapper to extract MAL data
    mal_scrapper = MALDataScrapper(baseurl="https://myanimelist.net/v1")

    # use existing token
    with open('ParamsAndHeaders/tokens.json') as tokens_file:
        tokens = json.load(tokens_file)

    # METHOD 1 for getting access tokens - store locally

    # if tokens doesnt exist or tokens expired
    if "expires_in" not in tokens.keys() or tokens['expires_in'] - req.get(f"https://worldtimeapi.org/api/timezone/{time_zone}").json()["unixtime"] <= 2:
        tokens = mal_scrapper.get_access_token(type='generate')
        print(f'generated tokens:\n\n {tokens}')

    # else refresh tokens (if necessary) for MAL auth
    elif tokens['expires_in'] - req.get(f"https://worldtimeapi.org/api/timezone/{time_zone}").json()["unixtime"] <= check_expiry_before:
        tokens = mal_scrapper.get_access_token(type='refresh')
        print(f'new tokens:\n\n {tokens}')

    # METHOD 2 for getting access tokens - store locally

    # create new log file
    number = createDirsObj.getIncrementedFileName(dir_name='LogFiles',
                                                  file_pattern='(EventLog-)([0-9]+)(.log)',
                                                  match_group=2)
    file_name = f'EventLog-{number}.log'

    # get prev batch no executed from latest log file
    if number > 0:
        with open(f'{os.getcwd()}\\LogFiles\\EventLog-{number-1}.log', 'r') as prev_log:
            last_line = prev_log.read().splitlines()[-1]
            batch = re.search('(batch:)([0-9]+)', last_line)
            b_no = None

            if batch:
                b_no = batch.groups()[1]

    # scrape anime list
    mal_scrapper.extract_anime_list(
        url='https://api.myanimelist.net/v2',
        query_string='fields=start_date,end_date,synopsis,mean,nsfw,rating,relations',
        token=tokens['access_token'],
        work_dir=os.getcwd(),
        log_file_path=f'LogFiles\\{file_name}',
        no_of_records=5, batches=1, start_idx=31500, time_constant=0.0032, prev_batch_no=b_no)

    # # connect and upload anime to database
    # print("uploading to DataBase Now .....\n\n")
    # time.sleep(2)

    # dbName = 'animeDB'
    # collection_name = 'animeCollection'
    # URI = os.getenv('URI')

    # uploadObj = animeUpload(dbName=dbName)

    # dbObj = uploadObj.connect_database(URI)

    # collectionItems = uploadObj.extract_anime(
    #     work_dir=f'{os.getcwd()}', batch_no=math.floor(30000/250))

    # uploadObj.add_to_collection(dbObj[collection_name], collectionItems)
