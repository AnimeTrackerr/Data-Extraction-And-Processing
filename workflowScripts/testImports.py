import os

# test imports
from Scrapper.MALDataScrapper import MALDataScrapper


# test env variables
vars = ['CLIENT_ID', 'CLIENT_SECRET', 'code',
        'code_verifier', 'refresh_token', 'PAT']

for var in vars:
    print(f'{var}: {os.environ[var]}')
