import os
import sys

# test imports
if sys.path.insert(0, os.path.abspath('..')):
    from Scrapper import MALDataScrapper

sys.path.insert(0, os.path.abspath('./workflowScripts'))

# test env variables
vars = ['CLIENT_ID', 'CLIENT_SECRET', 'code',
        'code_verifier', 'refresh_token', 'PAT']

for var in vars:
    print(f'{var}: {os.environ[var]}')
