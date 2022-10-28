import os

vars = ['CLIENT_ID', 'CLIENT_SECRET', 'CODE',
        'CODE_VERIFIER', 'REFRESH_TOKEN', 'PAT']


for var in vars:
    print(os.getenv(var))
