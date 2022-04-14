import os
import uuid
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
        # return {"status": "exists", "team_name": team_name}
        return CreateTeamResponse(status="exists", team_name=team_name)

    if owner is not None:
        if not owner['verified']:
            logging.info(f"The team owner has to link a league account !link <SummonerName>.")
            # return {"status": "not_verified", "disc_name": disc_name}
            return CreateTeamResponse(status="not_verified", disc_name=disc_name)
    else:
        logging.info(f"The team owner has to link a league account !link <SummonerName>.")
        # return {"status": "not_verified", "disc_name": disc_name}
        return CreateTeamResponse(status="not_verified", disc_name=disc_name)
    # New Team
    logging.info(f"Creating New Team {team_name}")
    new_team = {"name": team_name,
                "owner_id": disc_id,
                "member_ids": [disc_id],
                "invitation_ids": []}
    teams_collection.insert_one(new_team)
    # return {"status": "created", "team_name": team_name, "owner": owner}
    return CreateTeamResponse(status="created", team_name=team_name, owner=owner)


def invite_user(author, team_name, invitee):
    author_name = str(author)
    author_disc_id = author.id
    # find user_object
    invitee_id = invitee.id
    teamObj = teams_collection.find_one({"name": team_name})
    # verify that the given team name exists
    if teamObj is None:
        logging.info(f"The team {team_name} does not exist.")
        # return {"status": "team_notfound", "team_name": team_name}
        return InviteUserResponse(status="team_notfound", team_name=team_name)

    # check if the invitee is a verified user
    inviteeObj = collection.find_one({"discord_id": invitee_id})
    assert (inviteeObj != None)
    if not inviteeObj['verified']:
        logging.info(f"The user {invitee.name} is not verified.")
        # return {"status": "invitee_not_verified", "user_name": invitee.name}
        return InviteUserResponse(status="invitee_not_verified", user_name=invitee.name)

    if not teamObj['disc_id'] == author_disc_id:
        logging.info(f"Only the team owner is authorized to invite players.")
        # return {"status": "notowner"}
        return InviteUserResponse(status="notowner")

    ownerObj = collection.find_one({"discord_id": author_disc_id})
    assert (ownerObj['verified'])

    # New Invitee
    logging.info(f"Creating an invitation to team {team_name}.")

    teams_collection.update_one({"name": team_name},
                                {"$push": {
                                    "invitation_ids": invitee_id}})  # can be added as argument to create if list does not exist

    # return {"status": "success", "team_name": team_name, "invitee_name": invitee.name}
    return InviteUserResponse(status="success", team_name=team_name, invitee_name=invitee.name)


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
        # check if the author is invited
        if not authorObj in teamObj['invitees']:
            logging.info(f"The user {author_name} has not been invited to {team_name}.")
            # return {"status": "no_invitation", "user_name": author_name}
            return TeamJoinResponse(status="no_invitation", user_name=author_name)
        # if he is invited he has to be verified, thus we can invite him.    
        else:
            assert (authorObj['verified'])
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
        # return {"status": "team_notfound", "team_name": team_name}
        return TeamLeaveResponse(status="team_notfound", team_name=team_name)

    # check that the user is part of the team
    if not author_disc_id in teamObj['member_ids']:
        logging.info(f"The user {author_name} is not part of {team_name}.")
        # return {"status": "no_member", "user_name": author_name}
        return TeamLeaveResponse(status="no_member", user_name=author_name)
    else:
        # TODO: if the user is the team_owner the team_owner rights have to be transferred before leaving
        logging.info(f"{author_name} has left {team_name}.")
        teams_collection.update_one({"name": team_name},
                                    {"$pull": {"member_ids": author_disc_id}})
        # return {"status": "success", "team_name": team_name}
        return TeamLeaveResponse(status="success", team_name=team_name)


def remove_team(author, team_name):
    author_name = str(author)
    author_disc_id = author.id

    teamObj = teams_collection.find_one({"name": team_name})
    # verify that the given team name exists
    if teamObj is None:
        logging.info(f"The team {team_name} does not exist.")
        # return {"status": "team_notfound", "team_name": team_name}
        return TeamDeleteResponse(status="team_notfound", team_name=team_name)

    # check that the author is the team owner
    if not author_disc_id == teamObj['owner_id']:
        logging.info(f"Only the team owner is allowed to delete the team.")
        # return {"status": "not_owner", "user_name": author_name}
        return TeamDeleteResponse(status="not_owner", user_name=author_name)
    else:
        logging.info(f"{author_name} has deleted '{team_name}'.")
        teams_collection.delete_one({"name": team_name})
        # return {"status": "success", "team_name": team_name}
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
    return TeamShowResponse(status="success", teamObj=teamObj, members=players)


def get_all_teams(author):
    teamObj = teams_collection.find()
    # verify that the given team name exists
    teams = []
    for team in teamObj:
        teams.append(team)
    # return {"status": "success", "teams": teams}
    return TeamListResponse(status="success", teams=teams)


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

def join_match_asteam(user_id, match_id):
    # check if the author is owner of a team
    matchObj = match_collection.find_one({"_id": ObjectId(match_id)})
    # check that the team has not already entered the scrim    
    if (matchObj['team1'] != None and matchObj['team2'] != None):
        logging.info(f"Scrim is already full.")
        return {"status": "full"}
    teamObj = teams_collection.find({"owner_id": user_id})
    if (teamObj['name'] == matchObj['team1'] or teamObj['name'] == matchObj['team2']):
        logging.info(f"{teamObj['name']} is already part of the scrim.")
        return {"status": "already_part_of_it"}
    if teamObj is None:
        logging.info(f"{user_id} requested to join a scrim without owning a team.")
        return {"status": "not_owner"}
    else:
        logging.info(f"{teamObj['name']} joined the selected scrim at {matchObj['datetime']}.")
        matchDict  = get_match_byID(match_id) | {"status": "succcess"}
        return matchDict


def join_match_asplayer(user_id, match_id):
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
        matchDict['players_t1'][0].append(authorObj['summoner_name'])
        return {"status": "success", "match": matchObj, "players_t1": players_t1, "players_t2": players_t2}
    elif (team2_Obj is not None):
        logging.info(f"{user_id} joined scrim with id: {match_id}.")
        match_collection.update_one({"_id": ObjectId(match_id)},
                                    {"$push": {"roster2": user_id}})        
        matchDict['players_t2'].append(authorObj['summoner_name'])
        return {"status": "success", "match": matchObj, "players_t1": players_t1, "players_t2": players_t2}
    else:
        logging.info(f"{user_id} requested to join a scrim without being part of one of the teams.")
        return {"status": "no_member"}
