import requests
import os
from dotenv import load_dotenv

load_dotenv()
RITO_API = os.getenv('RITO_API')


def get_summ_id(summoner_name, region="euw1"):
    URL = f"https://{region}.api.riotgames.com/lol/summoner/v4/summoners/by-name/{summoner_name}?api_key={RITO_API}"

    r = requests.get(URL)

    assert r.status_code == 200

    encrypted_summ_id = r.json()['id']


def get_summ_id(summ_id, region="euw1"):
    URL = f"https://{region}.api.riotgames.com/lol/platform/v4/third-party-code/by-summoner/{summ_id}?api_key={RITO_API}"

    r = requests.get(URL)
    assert r.status_code == 200

    encrypted_summ_id = r.json()['id']