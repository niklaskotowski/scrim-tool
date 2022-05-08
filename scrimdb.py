import os
import uuid
from numpy import true_divide
from pymongo import MongoClient
import logging
from dotenv import load_dotenv
import requests
from bson.objectid import ObjectId
# client = MongoClient(os.getenv('MONGO_URI'))
from db.db_response import *
import db.lolapi_data as lol


load_dotenv()
client = MongoClient(os.getenv('MONGO_URI'))
db = client['scrimdb']
collection = db.users
teams_collection = db.teams
match_collection = db.matches


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
            # return {"status": "verified", "summoner_name": result['summoner_name']}
            return LinkResponse(status="verified", summoner_name=result['summoner_name'])
        # return {"status": "created", "verify": result['verification_id'], "summoner_name": result['summoner_name']}
        return LinkResponse(status="created", verification_id=result['verification_id'],
                            summoner_name=result['summoner_name'])

    summoner_result = collection.find_one({"summoner_name": summoner_name})
    if summoner_result is not None and summoner_result['verified']:  # Summoner Name already verified
        if disc_id != summoner_result['discord_id']:  # For different user
            # return {"status": "rejected"}
            return LinkResponse(status="rejected")
        # return {"status": "verified", "summoner_name": result['summoner_name']}
        return LinkResponse(status="verified", summoner_name=result['summoner_name'])

    summoner_id = get_summoner_id(summoner_name)
    if not summoner_id:  # Invalid Summoner Name
        # return {"status": "invalid"}
        return LinkResponse(status="invalid")

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
    # return {"status": "created", "verify": ver_id, "summoner_name": summoner_name}
    return LinkResponse(status="created", verification_id=ver_id, summoner_name=summoner_name)

    # client.close()


def rankedinfo_command(author):
    if not is_verified(author):
        return RankedInfoResponse(status="not_verified")

    disc_id = author.id
    result = collection.find_one({"discord_id": disc_id})

    if result is None:
        return RankedInfoResponse(status="error")

    data = lol.get_info(result["summoner_id"])
    return RankedInfoResponse(status="success", data=data)


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

def is_Owner(user_id):
    result = teams_collection.find_one({'owner_id': user_id})
    return result != None

def has_Team(user_id):
    result = teams_collection.find_one({"member_ids": {"$in": [user_id]}})
    print(result)
    return result != None

def get_UserByName(user_name):
    result = collection.fine_one({})

def get_all_Users():
    cursor = collection.find({})
    return cursor

def create_team(author, team_name):
    disc_name = author._json['user']['username']
    disc_id = int(author._json['user']['id'])

    team = teams_collection.find_one({"name": team_name})
    owner = collection.find_one({"discord_id": disc_id})

    if team is not None:
        logging.info(f"A team with this name already exists '{team_name}'")
        return CreateTeamResponse(status="exists", team_name=team_name)

    if owner is None or not owner['verified']:
        logging.info(f"The team owner has to link a league account !link <SummonerName>.")
        return CreateTeamResponse(status="not_verified", disc_name=disc_name)
    # New Team
    logging.info(f"Creating New Team {team_name}")
    new_team = {"name": team_name,
                "owner_id": disc_id,
                "member_ids": [disc_id],
                "invitation_ids": []}
    teams_collection.insert_one(new_team)
    return CreateTeamResponse(status="created", team_name=team_name, owner=owner)


def invite_user(author_id, team_id, invitee_id):
    # find user_object    
    teamObj = teams_collection.find_one({"_id": ObjectId(team_id)})
    if (invitee_id in teamObj['invitation_ids']):
        return InviteUserResponse(status="already_invited")
    # verify that the given team name exists
    if teamObj is None:
        logging.info(f"The team does not exist.")
        return InviteUserResponse(status="team_notfound")

    # check if the invitee is a verified user
    inviteeObj = collection.find_one({"discord_id": invitee_id})
    
    if not inviteeObj['verified']:
        logging.info(f"The user {invitee_id} is not verified.")
        return InviteUserResponse(status="invitee_not_verified", user_name=inviteeObj['discord_name'])

    if not teamObj['owner_id'] == author_id:
        logging.info(f"Only the team owner is authorized to invite players.")
        # return {"status": "notowner"}
        return InviteUserResponse(status="notowner")


    # New Invitee
    logging.info(f"Creating an invitation to team {team_id}.")

    teams_collection.update_one({"_id": ObjectId(team_id)},
                                {"$push": {
                                    "invitation_ids": invitee_id}})  # can be added as argument to create if list does not exist

    return InviteUserResponse(status="success", user_name=inviteeObj['discord_name'], team_name=teamObj['name'])


def join_team(author, team_name):
    author_name = str(author)
    author_disc_id = author.id

    teamObj = teams_collection.find_one({"name": team_name})
    # verify that the given team name exists
    if teamObj is None:
        logging.info(f"The team {team_name} does not exist.")
        # return {"status": "team_notfound", "team_name": team_name}
        return TeamJoinResponse(status="team_notfound", team_name=team_name)

    # check if author is verified
    authorObj = collection.find_one({"discord_id": author_disc_id})
    if authorObj is not None:
        print("check")
        # check if the author is invited
        if not author_disc_id in teamObj['invitation_ids']:
            logging.info(f"The user {author_name} has not been invited to {team_name}.")
            # return {"status": "no_invitation", "user_name": author_name}
            return TeamJoinResponse(status="no_invitation", user_name=author_name)
        # if he is invited he has to be verified, thus we can invite him.    
        else:
            assert (authorObj['verified'])
            print("test")
            logging.info(f"The user {author_name} has joined {team_name}.")
            teams_collection.update_one({"name": team_name},
                                        {"$pull": {"invitation_ids": author_disc_id}})
            teams_collection.update_one({"name": team_name},
                                        {"$push": {"member_ids": author_disc_id}})
            # return {"status": "success", "team_name": team_name}
            return TeamJoinResponse(status="success", team_name=team_name)
    else:
        logging.info(f"The user {author_name} has to be verified before interacting with teams.")
        # return {"status": "not_verified", "team_name": team_name}
        return TeamJoinResponse(status="not_verified", team_name=team_name)


def leave_team(author, team_name):
    author_name = str(author)
    author_disc_id = author.id

    teamObj = teams_collection.find_one({"name": team_name})
    # verify that the given team name exists
    if teamObj is None:
        logging.info(f"The team {team_name} does not exist.")
        return TeamLeaveResponse(status="team_notfound", team_name=team_name)

    # check that the user is part of the team
    if not author_disc_id in teamObj['member_ids']:
        logging.info(f"The user {author_name} is not part of {team_name}.")
        return TeamLeaveResponse(status="no_member", user_name=author_name)
    else:
        logging.info(f"{author_name} has left {team_name}.")
        teams_collection.update_one({"name": team_name},
                                    {"$pull": {"member_ids": author_disc_id}})
        return TeamLeaveResponse(status="success", team_name=team_name)


def remove_team(author, team_name):
    author_name = str(author)
    author_disc_id = author.id

    teamObj = teams_collection.find_one({"name": team_name})
    # verify that the given team name exists
    if teamObj is None:
        logging.info(f"The team {team_name} does not exist.")
        return TeamDeleteResponse(status="team_notfound", team_name=team_name)

    # check that the author is the team owner
    if not author_disc_id == teamObj['owner_id']:
        logging.info(f"Only the team owner is allowed to delete the team.")
        return TeamDeleteResponse(status="not_owner", user_name=author_name)
    else:
        logging.info(f"{author_name} has deleted '{team_name}'.")
        teams_collection.delete_one({"name": team_name})
        return TeamDeleteResponse(status="success", team_name=team_name)


def get_team(author, team_name):
    teamObj = teams_collection.find_one({"name": team_name})
    # verify that the given team name exists
    if teamObj is None:
        logging.info(f"The team {team_name} does not exist.")
        # return {"status": "team_notfound", "team_name": team_name}
        return TeamShowResponse(status="team_notfound", team_name=team_name)

    # get information about each player
    players = []
    for player_id in teamObj['member_ids']:
        players.append(collection.find_one({"discord_id": player_id}))
    logging.info(f"Team info for {team_name} has been successfully requested.")
    # return {"status": "success", "teamObj": teamObj, "members": players}
    return TeamShowResponse(status="success", team_name = teamObj['name'], teamObj=teamObj, members=players)

def getTeamByOwnerID(user_id):
    userObj = collection.find_one({"discord_id": user_id})
    if (userObj is None):
        return {"status": "not_verified"}
    teamObj = teams_collection.find_one({"owner_id": user_id})
    if (teamObj is not None):
        return {"status": "success", "team": teamObj}
    else:
        return {"status": "no_team"}

def getTeamByMemberID(user_id):
    userObj = collection.find_one({"discord_id": user_id})
    if (userObj is None):
        return {"status": "not_verified"}
    teamObj = teams_collection.find_one({"member_ids": {"$in": [user_id]}})
    if (teamObj is not None):
        return {"status": "success", "team": teamObj}
    else:
        return {"status": "no_team"}

def get_all_teams():
    teamObj = teams_collection.find()
    # verify that the given team name exists
    teams = []
    for team in teamObj:
        teams.append(team)
    if not teams:
        return TeamListResponse(status="no_team")
    return TeamListResponse(status="success", teams=teams)

def isPlayerInScrim(user_id, match_id):
    matchObj = match_collection.find_one({"_id": ObjectId(match_id)})
    if (user_id in matchObj['roster1'] or user_id in matchObj['roster2']):
        return True
    else:
        return False

def isTeamInScrim(team_name, match_id):
    matchObj = match_collection.find_one({"_id": ObjectId(match_id)})
    if (team_name == matchObj['team1'] or team_name == matchObj['team2']):
        return True
    else:
        return False

def create_match(author, team_name, datetime):
    disc_id = author.id
    # first verify that the given author owns the tean
    # a match entry in the collection is created and the first time is set to "team_name"
    teamObj = teams_collection.find_one({"name": team_name})
    if teamObj is None:
        logging.info(f"The team {team_name} does not exist.")
        return {"status": "team_notfound", "team_name": team_name}

    if teamObj['owner_id'] != disc_id:
        logging.info(f"Only the team owner can schedule a match.")
        return {"status": "not_owner", "team_name": team_name}

    new_match = {"datetime": datetime,
                 "team1": team_name,
                 "roster1": [],
                 "team2": None,
                 "roster2": []}

    match_collection.insert_one(new_match)
    return {"status": "created"}


def get_all_matches(author):
    matchObjects = match_collection.find()
    #obtain players for each match
    matches_ = []
    for match in matchObjects:   
        matches_.append(match)     
        players = []
        players_t1 = []
        players_t2 = []
        for p_id in match['roster1']:
            userObj = collection.find_one({"discord_id": p_id})
            players.append(userObj['summoner_name'])
        players_t1.append(players)
        players = []
        for p_id in match['roster2']:
            userObj = collection.find_one({"discord_id": p_id})
            players.append(userObj['summoner_name'])
        players_t2.append(players)

    return {"status" : "success", "matches" : matches_, "players_t1": players_t1, "players_t2": players_t2}


def get_match(author, team_name):
    teamObj = teams_collection.find({"name": team_name})
    if teamObj is None:
        logging.info(f"The team {team_name} does not exist.")
        return {"status": "team_notfound", "team_name": team_name}
    else:
        matches = match_collection.find({"$or" :[ {"team1": team_name}, {"team2": team_name} ] }) 
        print(matches)       
        players_1 = []
        players_2 = []   
        matches_ = []
        for match in matches:   
            matches_.append(match)     
            players = []
            for p_id in match['roster1']:
                userObj = collection.find_one({"discord_id": p_id})
                players.append(userObj['summoner_name'])
            players_1.append(players)
            players = []
            for p_id in match['roster2']:
                userObj = collection.find_one({"discord_id": p_id})
                players.append(userObj['summoner_name'])
            players_2.append(players)
        logging.info(f"Scheduled matches for {team_name} are returned.")
        return {"status": "success", "matches": matches_, "players_t1": players_1, "players_t2": players_2}

#return matchObj
#players_t1 summonername_vector of team one (if available)
#players_t2 summonername_vector of team two (if available)
def get_match_byID(match_id):
    matchObj = match_collection.find_one({"_id": ObjectId(match_id)})
    # verify that the author is not already part of one of the rosters
    players_t1 = []
    players_t2 = []
    p_1 = []
    p_2 = []
    for p_id in matchObj['roster1']:
        userObj = collection.find_one({"discord_id": p_id})
        p_1.append(userObj['summoner_name'])
    players_t1.append(p_1)
    for p_id in matchObj['roster2']:
        userObj = collection.find_one({"discord_id": p_id})
        p_2.append(userObj['summoner_name'])
    players_t2.append(p_2)
    return {"match": matchObj, "players_t1": players_t1, "players_t2": players_t2}

def join_match_asTeam(user_id, match_id):
    # check if the author is owner of a team
    matchObj = match_collection.find_one({"_id": ObjectId(match_id)})
    matchDict = ""
    # check that the team has not already entered the scrim    
    if (matchObj['team1'] != "" and matchObj['team2'] != ""):
        logging.info(f"Scrim is already full.")
        return {"status": "full"}
    teamObj = teams_collection.find_one({"owner_id": user_id})
    if teamObj is None:
        logging.info(f"{user_id} requested to join a scrim without owning a team.")
        return {"status": "not_owner"}
    if (teamObj['name'] == matchObj['team1'] or teamObj['name'] == matchObj['team2']):
        logging.info(f"{teamObj['name']} is already part of the scrim.")
        return {"status": "already_part_of_it"}
    if (matchObj['team1'] == ""):
        match_collection.update_one({"_id": ObjectId(match_id)},
                                    {"$set": {"team1": teamObj['name']}}) 
        logging.info(f"{teamObj['name']} joined the selected scrim at {matchObj['datetime']}.")
        matchDict  = get_match_byID(match_id) | {"status": "success"}
    if (matchObj['team2'] == ""):
        match_collection.update_one({"_id": ObjectId(match_id)},
                                    {"$set": {"team2": teamObj['name']}}) 
        logging.info(f"{teamObj['name']} joined the selected scrim at {matchObj['datetime']}.")
        matchDict  = get_match_byID(match_id) | {"status": "success"}
    return matchDict


def join_match_asPlayer(user_id, match_id):
    authorObj = collection.find_one({"discord_id": user_id})
    # here author['id'] as we obtain the author object from the reaction object
    # check if the author is part of one of the teams
    # how is this implemented in the most efficient way -- given the scrim _id verify that the author is either in team1 or team2
    # the roster recruiting starts when two teams have entered
    matchObj = match_collection.find_one({"_id": ObjectId(match_id)})
    # verify that the author is not already part of one of the rosters
    players_t1 = []
    players_t2 = []
    p_1 = []
    p_2 = []
    if matchObj is not None:        
        if (user_id in matchObj['roster1'] or user_id in matchObj['roster2']):
            logging.info(f"{user_id} is already part of the scrim.")
            return {'status': 'already_part_of_it'}
    else:
        return {'status': 'match_notfound'}
    matchDict = get_match_byID(match_id)
    team1_Obj = teams_collection.find_one({"name": matchDict['match']['team1'], "member_ids": {"$in": [user_id]}})
    team2_Obj = teams_collection.find_one({"name": matchDict['match']['team2'], "member_ids": {"$in": [user_id]}})
    if (team1_Obj is not None):
        logging.info(f"{user_id} joined scrim with id: {match_id}.")
        match_collection.update_one({"_id": ObjectId(match_id)},
                                    {"$push": {"roster1": user_id}}) 
        matchDict = {"status": "success"} | matchDict
        matchDict['players_t1'][0].append(authorObj['summoner_name'])
        return matchDict
    elif (team2_Obj is not None):
        logging.info(f"{user_id} joined scrim with id: {match_id}.")
        match_collection.update_one({"_id": ObjectId(match_id)},
                                    {"$push": {"roster2": user_id}}) 
        matchDict = {"status": "success"} | matchDict       
        matchDict['players_t2'].append(authorObj['summoner_name'])
        return matchDict
    else:
        logging.info(f"{user_id} requested to join a scrim without being part of one of the teams.")
        return {"status": "no_member"}

def leave_match_asTeam(user_id, match_id):
    # check if the author is owner of a team
    matchObj = match_collection.find_one({"_id": ObjectId(match_id)})
    # check that the team has already entered the scrim    
    teamObj = teams_collection.find_one({"owner_id": user_id})
    if (teamObj is not None and matchObj is not None):
        if (matchObj['team1'] == teamObj['name']):
            logging.info(f"The team {teamObj['name']} left the scrim.")
            match_collection.update_one({"_id": ObjectId(match_id)},
                                        {"$set": {"team1": ""}})
            match = get_match_byID(match_id)
            matchDict = {"status": "success"} | match
            return matchDict
        if (matchObj['team2'] == teamObj['name']):
            logging.info(f"The team {teamObj['name']} left the scrim.")
            match_collection.update_one({"_id": ObjectId(match_id)},
                                        {"$set": {"team2": ""}})
            match = get_match_byID(match_id)
            matchDict = {"status": "success"} | match
            return matchDict
    return {"status": "fail"}

def leave_match_asPlayer(user_id, match_id):
    # here author['id'] as we obtain the author object from the reaction object
    # check if the author is part of one of the teams
    # how is this implemented in the most efficient way -- given the scrim _id verify that the author is either in team1 or team2
    # the roster recruiting starts when two teams have entered
    matchObj = match_collection.find_one({"_id": ObjectId(match_id)})
    # verify that the author is not already part of one of the rosters
    if matchObj is not None:        
        if (user_id in matchObj['roster1']):
            logging.info(f"{user_id} has left a scrim.")
            match_collection.update_one({"_id": ObjectId(match_id)},
                            {"$pull": {"roster1": user_id}})  
            match = get_match_byID(match_id)
            return {'status': 'success'} | match
        if (user_id in matchObj['roster2']):
            logging.info(f"{user_id} has left a scrim.")
            match_collection.update_one({"_id": ObjectId(match_id)},
                            {"$pull": {"roster2": user_id}})  
            match = get_match_byID(match_id)
            return {'status': 'success'} | match
        return {'status': 'fail'}
    else:
        return {'status': 'fail'}
    