from Scrapper.MALDataScrapper import MALDataScrapper
import os
import sys
import requests as req
from base64 import b64encode
from nacl import encoding, public


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
    }

    for key, value in list_of_secrets:
        if key == 'expires_in':
            value = str(value + req.get(
                f"https://worldtimeapi.org/api/timezone/{os.getenv('T_ZONE')}").json()["unixtime"])

        data["encrypted_value"] = encrypt(key_info['key'], value)

        req.put(headers=headers, data=data,
                url=f"https://api.github.com/orgs/AnimeTrackerr/actions/secrets/{mapper[key]}")


if __name__ == "__main__":
    # GET NEW TOKENS
    gettokenObj = MALDataScrapper(url=None)

    data = {
        "code": os.getenv("code"),
        "code_verifier": os.getenv("code_verifier"),
        "refresh_token": os.getenv("refresh_token")
    }

    tokens = gettokenObj.get_access_token(
        type='refresh', save_and_get_locally=False, **data)

    # SET NEW TOKENS IN SECRETS

    # check if PAT is set
    try:
        print(type(os.environ['PAT']))
    except KeyError as ke:
        sys.exit(f'key not set: {ke}')

    # get the public key of the org
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {os.environ['PAT']}"
    }

    key_info = req.get(headers=headers,
                       url="https://api.github.com/orgs/AnimeTrackerr/actions/secrets/public-key").json()

    # encrypt and set the updated secrets
    secret_mapper = {
        'expires_in': 'EXPIRES_AT',
        'access_token': 'ACCESS_TOKEN',
        'refresh_token': 'REFRESH_TOKEN'
    }

    if "key_id" in key_info.keys():
        set_secrets(tokens, key_info, headers, **secret_mapper)
