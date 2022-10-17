import requests as req
import sys
import datetime
import os


try:
    days = int(os.environ['days'])
except KeyError as e:
    sys.exit("key error: 'days' env not set")

last_watch = (datetime.datetime.now() -
              datetime.timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%SZ")

res = req.get(
    f'https://api.github.com/repos/manami-project/anime-offline-database/commits?path=anime-offline-database.json&since={last_watch}').json()

if len(res) == 0:
    sys.exit(1)
else:
    sys.exit(0)
