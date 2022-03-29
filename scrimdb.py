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
teams_collection = db.teams

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

def create_team(author, team_name):
    print("in_db")
    disc_name = str(author)
    disc_id = author.id

    team = teams_collection.find_one({"name": team_name})
    print("in_coll1")
    owner = collection.find_one({"discord_id": disc_id})
    print("in_coll2")
    if team is not None:
        logging.info(f"A team with this name already exists '{team_name}'")
        return {"status": "exists", "team_name": team_name}       

    if owner is not None:
        if not owner['verified']:
            logging.info(f"The team owner has to link a league account !link <SummonerName>.")
            return {"status": "not_verified", "disc_name": disc_name}       
    else:
        logging.info(f"The team owner has to link a league account !link <SummonerName>.")
        return {"status": "not_verified", "disc_name": disc_name}    
    # New Team
    logging.info(f"Creating New Team {team_name}")
    new_team = {"name": team_name,
                "owner": owner,
                "member_ids": [disc_id],
                "invitation_ids": []}
    teams_collection.insert_one(new_team)
    return {"status": "created", "team_name": team_name, "owner": owner}

def invite_user(author, team_name, invitee):
    author_name = str(author)
    author_disc_id = author.id
    #find user_object
    invitee_id = invitee.id
    teamObj = teams_collection.find_one({"name": team_name})
    # verify that the given team name exists
    if teamObj is None:        
        logging.info(f"The team {team_name} does not exist.")
        return {"status": "team_notfound", "team_name": team_name}  

    # check if the invitee is a verified user
    inviteeObj = collection.find_one({"discord_id": invitee_id})
    assert(inviteeObj != None)
    if not inviteeObj['verified']:
        logging.info(f"The user {invitee.name} is not verified.")
        return {"status": "invitee_not_verified", "user_name": invitee.name}     

    if not teamObj['owner']['discord_id'] == author_disc_id:
        logging.info(f"Only the team owner is authorized to invite players.")
        return {"status": "notowner"} 

    ownerObj = collection.find_one({"discord_id": author_disc_id})
    assert(ownerObj['verified'])
 
    # New Invitee
    logging.info(f"Creating an invitation to team {team_name}.")

    teams_collection.update_one({"name": team_name},
                                {"$push": {"invitation_ids": invitee_id}}) # can be added as argument to create if list does not exist
    
    return {"status": "success", "team_name": team_name, "invitee_name": invitee.name}

def join_team(author, team_name):
    author_name = str(author)
    author_disc_id = author.id

    teamObj = teams_collection.find_one({"name": team_name})
    # verify that the given team name exists
    if teamObj is None:        
        logging.info(f"The team {team_name} does not exist.")
        return {"status": "team_notfound", "team_name": team_name}  

    # check if author is verified
    authorObj = collection.find_one({"discord_id": author_disc_id})
    if authorObj is not None:
        # check if the author is invited
        if not authorObj in teamObj['invitees']:
            logging.info(f"The user {author_name} has not been invited to {team_name}.")
            return {"status": "no_invitation", "user_name": author_name}
        # if he is invited he has to be verified, thus we can invite him.    
        else:
            assert(authorObj['verified'])
            logging.info(f"The user {author_name} has joined {team_name}.")
            teams_collection.update_one({"name": team_name},
                                        {"$pull": {"invitation_ids": author_disc_id}})        
            teams_collection.update_one({"name": team_name},
                                        {"$push": {"member_ids": author_disc_id}})
            return {"status": "success", "team_name": team_name}
    else:
        logging.info(f"The user {author_name} has to be verified before interacting with teams.")        
        return {"status": "not_verified", "team_name": team_name}
    

def leave_team(author, team_name):
    author_name = str(author)
    author_disc_id = author.id

    teamObj = teams_collection.find_one({"name": team_name})
    # verify that the given team name exists
    if teamObj is None:        
        logging.info(f"The team {team_name} does not exist.")
        return {"status": "team_notfound", "team_name": team_name}  

    # check that the user is part of the team
    if not author_disc_id in teamObj['member_ids']:
        logging.info(f"The user {author_name} is not part of {team_name}.")
        return {"status": "no_member", "user_name": author_name}      
    else:
        # TODO: if the user is the team_owner the team_owner rights have to be transferred before leaving
        logging.info(f"{author_name} has left {team_name}.")
        teams_collection.update_one({"name": team_name},
                                    {"$pull":{"member_ids": author_disc_id}})        
        return {"status": "success", "team_name": team_name}
    

def remove_team(author, team_name):  
    author_name = str(author)
    author_disc_id = author.id

    teamObj = teams_collection.find_one({"name": team_name})
    # verify that the given team name exists
    if teamObj is None:        
        logging.info(f"The team {team_name} does not exist.")
        return {"status": "team_notfound", "team_name": team_name}  

    # check that the author is the team owner
    if not author_disc_id == teamObj['owner']['discord_id']:
        logging.info(f"Only the team owner is allowed to delete the team.")
        return {"status": "not_owner", "user_name": author_name}      
    else:
        logging.info(f"{author_name} has deleted '{team_name}'.")
        teams_collection.delete_one({"name": team_name})
        return {"status": "success", "team_name": team_name}