import os
import sys
import requests as req
from base64 import b64encode
from nacl import encoding, public

if not sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..')):
    from Scrapper import MALDataScrapper


def encrypt(public_key: str, secret_value: str) -> str:

    public_key = public.PublicKey(
        public_key.encode("utf-8"), encoding.Base64Encoder())

    sealed_box = public.SealedBox(public_key)

    encrypted = sealed_box.encrypt(secret_value.encode("utf-8"))

    return b64encode(encrypted).decode("utf-8")


def set_secrets(list_of_secrets: dict, key_info: dict, headers: dict, **mapper) -> None:
    data = {
        "key_id": key_info['key_id'],
        "visibility": "selected",
        "selected_repository_ids": [551801562]
    }

    for key, value in list_of_secrets:
        data["encrypted_value"] = encrypt(key_info['key'], value)

        res = req.put(headers=headers, data=data,
                      url=f"https://api.github.com/orgs/AnimeTrackerr/actions/secrets/{mapper[key]}")

        if res.status_code != 204:
            print(f"Error setting key: {mapper[key]}")


if __name__ == "__main__":
    # GET NEW TOKENS
    gettokenObj = MALDataScrapper.MALDataScrapper(baseurl="https://myanimelist.net/v1")

    try:
        data = {
            "code": os.environ["code"],
            "code_verifier": os.environ["code_verifier"],
            "refresh_token": os.environ["refresh_token"]
        }
    except KeyError as ke:
        sys.exit(f'key not found: {ke}')

    tokens = gettokenObj.get_access_token(
        type='refresh', save_and_get_locally=False, **data)

    # SET NEW TOKENS IN SECRETS

    # get the public key of the org
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {os.environ['PAT']}"
    }

    key_info = req.get(headers=headers,
                       url="https://api.github.com/orgs/AnimeTrackerr/actions/secrets/public-key").json()

    # encrypt and set the updated secrets
    secret_mapper = {
        'expires_at': 'EXPIRES_AT',
        'access_token': 'MAL_ACCESS_TOKEN',
        'refresh_token': 'MAL_REFRESH_TOKEN'
    }

    if "key_id" in key_info.keys():
        set_secrets(tokens, key_info, headers, **secret_mapper)
