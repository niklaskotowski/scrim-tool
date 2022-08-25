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
import interactions


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
        return False

    verification = str(r.json())

    if verification == result['verification_id']:
        query = {"discord_id": disc_id,
                 "verification_id": verification}
        update = {"$set": {"verified": True}}
        collection.update_one(query, update)
        return True


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
    r = requests.get(URL)

    if r.status_code == 404:
        return False

    if r.status_code != 200:
        return "INVALID"

    return str(r.json()['id'])

def is_Owner(user_id):
    result = teams_collection.find_one({'owner_id': user_id})
    return result != None

def has_Team(user_id):
    result = teams_collection.find_one({"$or": [{"member_ids": {"$in": [user_id]}},
                                               {"owner_id": user_id}]})
    return result != None

def isPartofATeam(user_id):
    result = teams_collection.find_one({"member_ids": {"$in": [user_id]}})                                               
    return result != None

def isPartofTeamID(user_id, team_id):
    teamObj = teams_collection.find_one({"_id": ObjectId(team_id)})
    if user_id in teamObj['member_ids']:
        return True
    else:
        return False


def isInvitedIntoTeamID(user_id, team_id):
    teamObj = teams_collection.find_one({"_id": ObjectId(team_id)})
    if user_id in teamObj['invitation_ids']:
        return True
    else:
        return False

def hasPosibleInvitee(user_id, team_id):
    teamObj = teams_collection.find_one({"_id": ObjectId(team_id)})
    teams = teams_collection.find()
    member_ids = [x['member_ids'] for x in teams]
    print(member_ids)
    x = [x for x in member_ids]
    print(x)
    all_member_ids = sum(x, [])
    userObjs = collection.find()
    print(member_ids)
    for usr in userObjs:
        if not usr['discord_id'] in teamObj['invitation_ids'] and not usr['discord_id'] in all_member_ids and usr['discord_id'] != user_id:
            return True
    return False

def get_UserByName(user_name):
    result = collection.fine_one({})

def get_all_Users():
    cursor = collection.find({})
    return cursor

# returns users that can be invited
def get_all_validUsers(team_id):    
    team = teams_collection.find_one({'_id': team_id})
    cursor = collection.find({"$and": [{'discord_id': {"$nin": team['invitation_ids']}},
                                       {'discord_id': {"$ne": team['owner_id']}},
                                       {'discord_id': {"$nin": team['member_ids']}}]})
    return cursor

def getMatchbyMatchID(match_id):
    return match_collection.find_one({'_id': match_id})

def getMatchbyTeamIDs(team_id1, team_id2):
    return match_collection.find_one({"$or": [{'$and' : [{'team1' : team_id1}, {'team2': team_id2}]},
                                              {'$and' : [{'team2' : team_id1}, {'team1': team_id2}]}]}                  )

def getTeamByTeamID(team_id):
    return teams_collection.find_one({'_id': team_id})

def getTeamByTeamName(team_name):
    return teams_collection.find_one({'name': team_name})

def get_Team_Embed(team_id):
    teamObj = getTeamByTeamID(team_id)
    member_ids = [x for x in teamObj['member_ids']]
    db_response = getUsersByIDs(member_ids)
    user_Objects = db_response['userObjects']
    member_list = ["[" + str(x['discord_name'].split("#")[0]) + "]" + "(https://euw.op.gg/summoners/euw/" + str(x['summoner_name']) + ")\n" for x in user_Objects]
    member_string = "".join(member_list)
    playerField = interactions.EmbedField(
        name="Member: ",
        value=member_string,
        inline=True,
    )
    statisticsField = interactions.EmbedField(
        name="Statistics: ",
        value='Wins: 6, Defeats: 9',
        inline=True,
    )
    embed=interactions.Embed(title=" ", color=2, description="Team Hub (" +  teamObj['name'] + ")", fields=[playerField, statisticsField])
    return embed

def get_Team_Embed_Buttons(team_id, user_id):
    teamObj = getTeamByTeamID(team_id)
    member_ids = [x for x in teamObj['member_ids']]
    invitee_ids = [x for x in teamObj['invitation_ids']]
    db_response = getUsersByIDs(member_ids)    
    user_Objects = db_response['userObjects']
    db_response = getUsersByIDs(invitee_ids)
    invitee_Objects = db_response['userObjects']
    member_list = ["[" + str(x['discord_name'].split("#")[0]) + "]" + "(https://euw.op.gg/summoners/euw/" + str(x['summoner_name']) + ")\n" for x in user_Objects]
    invitee_list = ["[" + str(x['discord_name'].split("#")[0]) + "]" + "(https://euw.op.gg/summoners/euw/" + str(x['summoner_name']) + ")\n" for x in invitee_Objects]
    member_string = "".join(member_list)
    invitee_string = "".join(invitee_list)
    if member_string == "":
        member_string = "Empty"
    if invitee_string == "":
        invitee_string = "No invitations"

    playerField = interactions.EmbedField(
        name="Member: ",
        value=member_string,
        inline=True,
    )
    statisticsField = interactions.EmbedField(
        name="Statistics: ",
        value='Wins: 6, Defeats: 9',
        inline=True,
    )
    inviteesField = interactions.EmbedField(
        name="Invitees: ",
        value=invitee_string,
        inline=True,
    )
    embed=interactions.Embed(title=" ", color=3, description="Team Hub (" +  teamObj['name'] + ")", fields=[playerField, inviteesField, statisticsField])    
    invite_MemberBT = interactions.Button(
        style=interactions.ButtonStyle.SECONDARY,
        label="Invite User",
        custom_id="invite_User"
    )
    leave_TeamBT = interactions.Button(
        style=interactions.ButtonStyle.SECONDARY,
        label="Leave",
        custom_id="leave_Team"
    )
    join_TeamBT = interactions.Button(
        style=interactions.ButtonStyle.SECONDARY,
        label="Join",
        custom_id="join_Team"
    )
    deleteTeamBT = interactions.Button(
        style=interactions.ButtonStyle.SECONDARY,
        label="Delete",
        custom_id="delete_Team"
    )
    homeTeamBT = interactions.Button(
        style=interactions.ButtonStyle.SUCCESS,
        label="Home",
        custom_id="home_button"
    )
    if (is_Owner(user_id) and isPartofTeamID(user_id, teamObj['_id'])):        
        if(hasPosibleInvitee(user_id, teamObj['_id'])):
            buttons = [invite_MemberBT, leave_TeamBT, deleteTeamBT]
        else:
            buttons = [leave_TeamBT, deleteTeamBT]
    elif(is_Owner(user_id) and not isPartofTeamID(user_id, teamObj['_id'])):
        if(hasPosibleInvitee(user_id, teamObj['_id'])):
            buttons = [invite_MemberBT, join_TeamBT, deleteTeamBT]
        else:
            buttons = [join_TeamBT, deleteTeamBT]
    elif(isPartofTeamID(user_id, teamObj['_id']) and not is_Owner(user_id)):
        buttons = [leave_TeamBT]
    elif(not isPartofTeamID(user_id, teamObj['_id']) and isInvitedIntoTeamID(user_id, teamObj['_id'])):
        buttons = [join_TeamBT]
    else:
        buttons = []
    buttons.append(homeTeamBT)
    row = interactions.ActionRow(components = buttons) 
    return embed, row

        
def get_Match_Embed_Buttons(match_id, user_id):
    #a team member not owning the team can only see the match up
    matchObj = getMatchbyMatchID(match_id)
    team1_id = matchObj['team1']
    team2_id = matchObj['team2']
    team1 = getTeamByTeamID(team1_id)
    team2 = getTeamByTeamID(team2_id)  
    roster1 = getUsersByIDs(matchObj['roster1'])['userObjects']
    roster2 = getUsersByIDs(matchObj['roster2'])['userObjects']
    roster1_list = ["[" + str(x['discord_name'].split("#")[0]) + "]" + "(https://euw.op.gg/summoners/euw/" + str(x['summoner_name']) + ")\n" for x in roster1]
    roster2_list = ["[" + str(x['discord_name'].split("#")[0]) + "]" + "(https://euw.op.gg/summoners/euw/" + str(x['summoner_name']) + ")\n" for x in roster2]    
    roster1_string = "".join(roster1_list)
    roster2_string = "".join(roster2_list)
    team_1_name = team1['name'] if team1 else "Open"
    team_2_name = team2['name'] if team2 else "Open"
    if roster1_string == "":
        roster1_string = "Empty"
    if roster2_string == "":
        roster2_string = "Empty"
    roster1Field = interactions.EmbedField(
        name="Member: ",
        value=roster1_string,
        inline=False,
    )
    overviewField = interactions.EmbedField(
        name="Scrim Match - " + str(team_1_name) + " vs. " + str(team_2_name),
        value=str("___"),
        inline=True,    
    )
    roster2Field = interactions.EmbedField(
        name="Member: ",
        value=roster2_string,
        inline=False,
    )
    embed=interactions.Embed(title=" ", color=3, description="Scrim Match (" + str(team_1_name) + " - " + str(team_2_name) + ")", fields=[overviewField, roster1Field, roster2Field])    
    leave_MatchBT = interactions.Button(
        style=interactions.ButtonStyle.SECONDARY,
        label="Leave as Player",
        custom_id="leave_Match"
    )
    join_MatchBT = interactions.Button(
        style=interactions.ButtonStyle.SECONDARY,
        label="Join as Player",
        custom_id="join_Match"
    )
    leave_MatchTeam_BT = interactions.Button(
        style=interactions.ButtonStyle.PRIMARY,
        label="Leave as Team",
        custom_id="leave_Match_asTeam"
    )
    join_MatchTeam_BT = interactions.Button(
        style=interactions.ButtonStyle.PRIMARY,
        label="Join as Team",
        custom_id="join_Match_asTeam"
    )
    homeTeamBT = interactions.Button(
        style=interactions.ButtonStyle.SUCCESS,
        label="Home",
        custom_id="home_button"
    )
    #we can only join a match if there are two teams ready - this rule is requiered for consistent use
    both_teams = matchObj['team1'] != None and matchObj['team2'] != None
    if ((isPartofTeamID(user_id, team1_id) or isPartofTeamID(user_id, team2_id)) and both_teams):        
        buttons= [join_MatchBT, leave_MatchBT]
    elif(is_Owner(user_id) and (isPartofTeamID(user_id, team1_id) or isPartofTeamID(user_id, team2_id))):
        buttons = [join_MatchBT, leave_MatchBT, leave_MatchTeam_BT]
    elif(is_Owner(user_id) and not (isPartofTeamID(user_id, team1_id) or isPartofTeamID(user_id, team2_id)) and not both_teams):
        buttons = [join_MatchBT, leave_MatchBT, join_MatchTeam_BT] 
    else:
        buttons = []
    buttons.append(homeTeamBT)
    row = interactions.ActionRow(components = buttons) 
    return embed, row
    
def create_team(author, team_name):
    disc_name = author._json['user']['username']
    disc_id = int(author._json['user']['id'])

    team = teams_collection.find_one({"name": team_name})
    owner = collection.find_one({"discord_id": disc_id})

    if team is not None:
        return 
    if owner is None or not owner['verified']:
        return 
        
    # New Team
    new_team = {"name": team_name,
                "owner_id": disc_id,
                "member_ids": [disc_id],
                "invitation_ids": []}
    teams_collection.insert_one(new_team)
    teamObj = getTeamByOwnerID(disc_id)
    return teamObj['team']


def invite_user(author_id, team_id, invitee_id):
    # find user_object    
    teamObj = teams_collection.find_one({"_id": ObjectId(team_id)})
    if (invitee_id in teamObj['invitation_ids']):
        return InviteUserResponse(status="already_invited")
    # verify that the given team name exists
    if teamObj is None:
        return InviteUserResponse(status="team_notfound")

    # check if the invitee is a verified user
    inviteeObj = collection.find_one({"discord_id": invitee_id})
    
    if not inviteeObj['verified']:
        return InviteUserResponse(status="invitee_not_verified", user_name=inviteeObj['discord_name'])

    if not teamObj['owner_id'] == author_id:
        return InviteUserResponse(status="notowner")

    teams_collection.update_one({"_id": ObjectId(team_id)},
                                {"$push": {
                                    "invitation_ids": invitee_id}})  # can be added as argument to create if list does not exist

    return InviteUserResponse(status="success", user_name=inviteeObj['discord_name'], team_name=teamObj['name'])


def join_team(user_id, team_id):
    teamObj = teams_collection.find_one({"_id": ObjectId(team_id)})

    teams_collection.update_one({"_id": ObjectId(team_id)},
                                {"$pull": {"invitation_ids": user_id}})
    teams_collection.update_one({"_id": ObjectId(team_id)},
                                {"$push": {"member_ids": user_id}})
    # return {"status": "success", "team_name": team_name}
    return teamObj


def leave_team(author_id, team_id):
    teamObj = teams_collection.find_one({"_id": team_id})
    # verify that the given team name exists
    if teamObj is None:
        return False
    # check that the user is part of the team
    if not author_id in teamObj['member_ids']:
        return False
    else:
        teams_collection.update_one({"_id": team_id},
                                    {"$pull": {"member_ids": author_id}})
    return teamObj


def remove_team(author_id, team_id):
    teamObj = teams_collection.find_one({"_id": team_id})
    # verify that the given team name exists
    if teamObj is None:
        return TeamDeleteResponse(status="team_notfound", team_id=team_id)

    # check that the author is the team owner
    if not author_id == teamObj['owner_id']:
        return TeamDeleteResponse(status="not_owner", user_id=author_id)
    else:
        teams_collection.delete_one({"_id": team_id})
        return TeamDeleteResponse(status="success", team_id=team_id)


def get_team(author, team_name):
    teamObj = teams_collection.find_one({"name": team_name})
    # verify that the given team name exists
    if teamObj is None:
        # return {"status": "team_notfound", "team_name": team_name}
        return TeamShowResponse(status="team_notfound", team_name=team_name)

    # get information about each player
    players = []
    for player_id in teamObj['member_ids']:
        players.append(collection.find_one({"discord_id": player_id}))
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

def getUsersByIDs(user_ids):
    userObjects = []
    for user_id in user_ids:
        userObj = collection.find_one({"discord_id": user_id})
        userObjects.append(userObj)
    if (userObjects is []):
        return {"status": "no_users_found"}
    else:
        return {"status": "success", "userObjects": userObjects}

def get_all_teams():
    teamObjs = teams_collection.find()
    # verify that the given team name exists
    teams = []
    for team in teamObjs:
        teams.append(team)
    return teams

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

def create_match(team_id, datetime):    
    # first verify that the given author owns the tean
    # a match entry in the collection is created and the first time is set to "team_name"
    teamObj = teams_collection.find_one({"_id": team_id})
    if teamObj is None:
        return {"status": "team_notfound", "team_id": team_id}
    new_match = {"datetime": datetime,
                 "team1": team_id,
                 "roster1": [],
                 "team2": None,
                 "roster2": []}

    match_collection.insert_one(new_match)
    match_id = getMatchbyTeamIDs(team_id, None)
    return match_id


def get_all_matches():
    matchObjs = match_collection.find()
    # verify that the given team name exists
    matches = []
    for match in matchObjs:
        matches.append(match)
    return matches


def get_match(author, team_name):
    teamObj = teams_collection.find({"name": team_name})
    if teamObj is None:
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
        return {"status": "full"}
    teamObj = teams_collection.find_one({"owner_id": user_id})
    if teamObj is None:
        return {"status": "not_owner"}
    if (teamObj['name'] == matchObj['team1'] or teamObj['name'] == matchObj['team2']):
        return {"status": "already_part_of_it"}
    if (matchObj['team1'] == ""):
        match_collection.update_one({"_id": ObjectId(match_id)},
                                    {"$set": {"team1": teamObj['name']}}) 
        matchDict  = get_match_byID(match_id) | {"status": "success"}
    if (matchObj['team2'] == ""):
        match_collection.update_one({"_id": ObjectId(match_id)},
                                    {"$set": {"team2": teamObj['name']}}) 
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
            return {'status': 'already_part_of_it'}
    else:
        return {'status': 'match_notfound'}
    matchDict = get_match_byID(match_id)
    team1_Obj = teams_collection.find_one({"_id": matchDict['match']['team1'], "member_ids": {"$in": [user_id]}})
    team2_Obj = teams_collection.find_one({"_id": matchDict['match']['team2'], "member_ids": {"$in": [user_id]}})
    if (team1_Obj is not None):
        match_collection.update_one({"_id": ObjectId(match_id)},
                                    {"$push": {"roster1": user_id}}) 
        matchDict['players_t1'][0].append(authorObj['summoner_name'])
        return matchDict
    elif (team2_Obj is not None):
        match_collection.update_one({"_id": ObjectId(match_id)},
                                    {"$push": {"roster2": user_id}})  
        matchDict['players_t2'].append(authorObj['summoner_name'])
        return matchDict
    else:
        return {"status": "no_member"}

def leave_match_asTeam(user_id, match_id):
    # check if the author is owner of a team
    matchObj = match_collection.find_one({"_id": ObjectId(match_id)})
    # check that the team has already entered the scrim    
    teamObj = teams_collection.find_one({"owner_id": user_id})
    if (teamObj is not None and matchObj is not None):
        if (matchObj['team1'] == teamObj['_id']):
            match_collection.update_one({"_id": ObjectId(match_id)},
                                        {"$set": {"team1": ""}})
            match = get_match_byID(match_id)
            return match
        if (matchObj['team2'] == teamObj['_id']):
            match_collection.update_one({"_id": ObjectId(match_id)},
                                        {"$set": {"team2": ""}})
            match = get_match_byID(match_id)
            return match
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
            match_collection.update_one({"_id": ObjectId(match_id)},
                            {"$pull": {"roster1": user_id}})  
            match = get_match_byID(match_id)
            return match
        if (user_id in matchObj['roster2']):
            match_collection.update_one({"_id": ObjectId(match_id)},
                            {"$pull": {"roster2": user_id}})  
            match = get_match_byID(match_id)
            return match
        return {'status': 'fail'}
    else:
        return {'status': 'fail'}
