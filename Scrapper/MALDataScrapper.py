import secrets
import json
import os
import requests as req
from requests import HTTPError
from tqdm import tqdm
import re
import time


class MALDataScrapper:
    def __init__(self, baseurl):
        self.baseurl = baseurl

    def get_new_code_verifier(self) -> str:
        token = secrets.token_urlsafe(100)
        return token[:64]

    def authorize(self, generate_code_verifier=True):
        # generate new code verifier
        if generate_code_verifier:
            os.environ['code'] = self.get_new_code_verifier()

            with open('ParamsAndHeaders/code_verifier.json', 'w', encoding='utf-8') as code_verifier_file:
                json.dump(
                    {'code_verifier': os.environ['code']}, code_verifier_file)

        # use from existing one
        else:
            with open('ParamsAndHeaders/code_verifier.json', 'r') as code_verifier_file:
                os.environ['code'] = json.load(code_verifier_file)[
                    'code_verifier']

        params = {}
        params["response_type"] = "code"
        params["client_id"] = os.getenv('CLIENT_ID')
        params["code_challenge"] = os.getenv('code')

        param_string = f''

        for key, value in params.items():
            param_string += f'{key}={value}&'

        print(
            f'\nopen link to to generate code: {self.baseurl}/oauth2/authorize?{param_string}\n')

        code = input("\nenter the code: ")

        return code

    def get_access_token(self, type='generate'):
        # define or get body values
        data = {}

        data['client_id'] = os.getenv('CLIENT_ID')
        data['client_secret'] = os.getenv('CLIENT_SECRET')

        if type == 'generate':
            # authorize and generate code
            code = self.authorize()

            data['grant_type'] = 'authorization_code'
            data['code'] = code
            data['code_verifier'] = os.getenv('code')

            with open('ParamsAndHeaders/code.json', 'w') as code_file:
                json.dump({'code': data['code']}, code_file)

        else:
            data['grant_type'] = 'refresh_token'

            with open('ParamsAndHeaders/code.json', 'r') as code_file:
                data['code'] = json.load(code_file)['code']

            with open('ParamsAndHeaders/code_verifier.json', 'r') as code_verifier_file:
                data['code_verifier'] = json.load(code_verifier_file)[
                    'code_verifier']

            with open('ParamsAndHeaders/tokens.json', 'r') as tokens_file:
                data['refresh_token'] = json.load(tokens_file)['refresh_token']

        # make a request
        try:
            res = req.post(f'{self.baseurl}/oauth2/token', data=data).json()
        except HTTPError as weberr:
            return f'Error: {weberr}'

        # extract tokens
        tokens = {}
        tokens['access_token'] = res["access_token"]
        tokens['refresh_token'] = res["refresh_token"]
        tokens['expires_in'] = req.get(
            f"https://worldtimeapi.org/api/timezone/{os.getenv('T_ZONE')}").json()["unixtime"] + res["expires_in"]

        # save the tokens
        with open('ParamsAndHeaders/tokens.json', 'w') as tokens_file:
            json.dump(tokens, tokens_file)

        # return tokens
        return tokens

    def get_anime_info(self, url, anime_id, query_string, token):
        url = f'{url}/anime/{anime_id}?{query_string}'

        try:
            return req.get(url, headers={
                'Authorization': f'Bearer {token}'
            })

        except HTTPError as e:
            print(f'error: {e}')
            return None

    def extract_anime_list(self, url, query_string, token, work_dir, log_file_path, no_of_records=10, batches=1, start_idx=0, time_constant=0.02, prev_batch_no=None):
        patterns = '\"|“'

        key_mapper = {
            'mean': 'malScore',
            'start_date': 'startDate',
            'end_date': 'endDate',
            'nsfw': 'nsfw',
            'rating': 'rating',
            'synopsis': 'synopsis'
        }

        with open('RawData/anime_data.json', 'r') as anime_data_file:
            anime_data = json.load(anime_data_file)

            if start_idx >= len(anime_data):
                return

            start = start_idx//no_of_records

            prev_batch_no = prev_batch_no or start

            for b_i in tqdm(range(start, start + batches), desc='batches processed', unit='bat'):
                combined_data = []
                checked = set()
                page_not_found = anime_added = mal_absent = 0

                with open(f'{work_dir}\\CombinedAnimeData\\animedata({start_idx}-{start_idx + no_of_records}).json', 'w', encoding='utf-8') as combined_data_file:

                    for anime in tqdm(anime_data[start_idx: start_idx + no_of_records], desc='anime processed', unit='anime', leave=False):
                        matched = 0

                        anime["synonyms"] = re.sub(patterns, "", f'{anime["title"]} ') + ' '.join(
                            re.sub(patterns, "", synonym) for synonym in anime["synonyms"])
                        anime['startDate'] = \
                            anime['endDate'] = \
                            anime['synopsis'] = \
                            anime['malScore'] = \
                            anime['nsfw'] = \
                            anime['rating'] = None
                        anime['relations'] = []

                        for link in anime['sources']:
                            match = re.match(
                                "(https://myanimelist.net/anime/)([0-9]+)", link)

                            if match:
                                matched = 1

                                try:
                                    anime_id = match.groups()[1]

                                    # process anime malID and synonyms
                                    anime['malID'] = anime_id

                                    if anime_id in checked:
                                        continue

                                    checked.add(anime_id)

                                    res = self.get_anime_info(
                                        url, anime_id, query_string, token)

                                    data, stat_code = res.json(), res.status_code

                                    if stat_code == 200:

                                        for key in key_mapper:
                                            try:
                                                if key == 'start_date' or key == 'end_date':
                                                    anime[key_mapper[key]] = {
                                                        '$date': data[key]}
                                                else:
                                                    anime[key_mapper[key]
                                                          ] = data[key]

                                            except KeyError:
                                                continue    # error already handled by initializing anime object to None

                                    elif stat_code == 404:
                                        page_not_found += 1

                                except AttributeError as e:
                                    print(f'ERROR: {e}')

                                break

                        if matched == 0:
                            mal_absent += 1

                        combined_data.append(anime)
                        anime_added += 1

                    start_idx += no_of_records

                    json.dump(combined_data, combined_data_file)

                log_message = f'T:{time.ctime()}\t  batch:{b_i + 1} ; anime added:{anime_added}/{no_of_records} ; MAL absent:{mal_absent}/{no_of_records} ; page not found:{page_not_found}\n'

                # create a log file
                with open(f'{work_dir}\\{log_file_path}', 'a') as log_file:
                    log_file.write(log_message)

                # time gap for the onslaught of requests
                time.sleep(time_constant * (b_i + 1) * no_of_records)
