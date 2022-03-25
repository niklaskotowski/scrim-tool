import os
import uuid
from pymongo import MongoClient
import logging
from dotenv import load_dotenv
import requests

#client = MongoClient(os.getenv('MONGO_URI'))

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [%(name)s] [%(levelname)s] - %(message)s',
                    datefmt='%m/%d/%Y %H:%M:%S',
                    handlers=[
                        logging.FileHandler("scrimdb.log"),
                        logging.StreamHandler()
                    ])

load_dotenv()
client = MongoClient(os.getenv('MONGO_URI'))
db = client['scrimdb']
collection = db.users

def unlink_command(author):
    result = collection.delete_many({"discord_id": author.id})
    return result.deleted_count

def link_command(summoner_name, author):
    disc_name = str(author)
    disc_id = author.id

    result = collection.find_one({"discord_id": disc_id})

    if result is not None:
        if not result['verified']:
            check_verification(author)
        if result['verified']:
            logging.info(f"{disc_name} already has verified Summoner '{result['summoner_name']}'")
            return {"status": "verified", "summoner_name": result['summoner_name']}
        return {"status": "created", "verify": result['verification_id'], "summoner_name": result['summoner_name']}

    summoner_result = collection.find_one({"summoner_name": summoner_name})
    if summoner_result is not None and summoner_result['verified']:  # Summoner Name already verified
        if disc_id != summoner_result['discord_id']:  # For different user
            return {"status": "rejected"}
        return {"status": "verified", "summoner_name": result['summoner_name']}

    summoner_id = get_summoner_id(summoner_name)
    if not summoner_id: # Invalid Summoner Name
        return {"status": "invalid"}

    # New User
    logging.info(f"Creating New User {disc_name}")
    ver_id = str(uuid.uuid4())

    new_user = {"discord_name": disc_name,
                "discord_id": disc_id,
                "summoner_name": summoner_name,
                "verification_id": ver_id,
                "summoner_id": summoner_id,
                "verified": False}

    collection.insert_one(new_user)
    return {"status": "created", "verify": ver_id, "summoner_name": summoner_name}

    #client.close()

def check_verification(author, region="euw1"):
    disc_id = author.id
    result = collection.find_one({"discord_id": disc_id})

    if result is None:
        return False

    URL = f"https://{region}.api.riotgames.com/lol/platform/v4/third-party-code" \
          f"/by-summoner/{result['summoner_id']}?api_key={os.getenv('RIOT_API')}"
    r = requests.get(URL)

    if r.status_code != 200:
        logging.warning(f"Failed to verify for Summoner '{result['summoner_name']}' - {r.status_code}")
        return False

    verification = str(r.json())

    if verification == result['verification_id']:
        query = {"discord_id": disc_id,
                "verification_id": verification}
        update = {"$set": {"verified": True}}
        collection.update_one(query, update)
        logging.info(f"Summoner '{result['summoner_name']}' is now verified for {result['discord_name']}")
        return True
    else:
        logging.warning("Verification is complete but IDs do not match")


def is_verified(author):
    disc_id = author.id
    result = collection.find_one({"discord_id": disc_id})

    if result is None:
        return False

    if not result['verified']:
        return False

    return True


def get_summoner_id(summoner_name, region="euw1"):
    URL = f"https://{region}.api.riotgames.com/lol/summoner/v4/summoners/by-name/{summoner_name}?api_key={os.getenv('RIOT_API')}"
    logging.info(f"RIOT API CALL - {URL}")
    r = requests.get(URL)

    if r.status_code == 404:
        logging.warning(f"Summoner {summoner_name} does not exist")
        return False

    if r.status_code != 200:
        logging.error(f"Failed to fetch summoner id for {summoner_name} - {r.status_code}")
        logging.error(r.json())
        return "INVALID"

    return str(r.json()['id'])