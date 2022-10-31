import sys
import os

if not sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..')):
    from Scrapper import MALDataScrapper

# test imports
print(MALDataScrapper)

# # test env variables
vars = ['CLIENT_ID', 'CLIENT_SECRET', 'code',
        'code_verifier', 'refresh_token', 'PAT']

for var in vars:
    print(f'{var}: {os.environ[var]}')
