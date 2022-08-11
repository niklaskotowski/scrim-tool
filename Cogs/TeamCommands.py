from code import interact
from attr import field
import discord
from discord.ext import commands
import scrimdb as db
import logging
import interactions
from bson.objectid import ObjectId
import datetime


exit = 	"\u274C"
check = "\u2705"
action_stack = []

invitationMap = ['______________', 'Open Invitation']

class TeamCommands(interactions.Extension):
    def __init__(self, client):
        self.client: interactions.Client = client

    #team overview command
    @interactions.extension_command(
        name="team_overview",
        description="Scrim Tool",
        scope=271639846307627008,
    )
    async def team_overview(self, ctx):
        user_id = int(ctx.author._json['user']['id'])
        if (not db.has_Team(user_id)):
            main_TeamBT = interactions.Button(
                style=interactions.ButtonStyle.SECONDARY,
                label="Create Team",
                custom_id="create_t"
            )
        else:
            main_TeamBT = interactions.Button(
                style=interactions.ButtonStyle.SECONDARY,
                label="Team Hub",
                custom_id="show_myTeam"
            )
        existTeams = len(db.get_all_teams()) == 0
        #TODO for existMatches
        show_TeamsBT = interactions.Button(
            style=interactions.ButtonStyle.SECONDARY,
            label="Show Teams",
            custom_id="show_teams",
            disabled=existTeams
        )
        show_MatchesBT = interactions.Button(
            style=interactions.ButtonStyle.SECONDARY,
            label="Show Matches",
            custom_id="show_matches",
            disabled=False
        )
        if (db.is_Owner(user_id)):
            create_matchBT = interactions.Button(
                style=interactions.ButtonStyle.SECONDARY,
                label="Create Match",
                custom_id="selectDayForMatch"
            )        
            row = interactions.ActionRow(components = [main_TeamBT, show_TeamsBT, create_matchBT, show_MatchesBT]) 
        else:
            row = interactions.ActionRow(components = [main_TeamBT, show_TeamsBT, show_MatchesBT]) 
        await ctx.send("Scrim Tool:", components=row, ephemeral=True)

    #Home Button
    async def home_button(self, ctx):
        user_id = int(ctx.author._json['user']['id'])
        if (not db.has_Team(user_id)):
            main_TeamBT = interactions.Button(
                style=interactions.ButtonStyle.SECONDARY,
                label="Create Team",
                custom_id="create_t"
            )
        else:
            main_TeamBT = interactions.Button(
                style=interactions.ButtonStyle.SECONDARY,
                label="Team Hub",
                custom_id="show_myTeam"
            )
        existTeams = len(db.get_all_teams()) >= 1
        show_TeamsBT = interactions.Button(
            style=interactions.ButtonStyle.SECONDARY,
            label="Show Teams",
            custom_id="show_teams",
            disabled=existTeams
        )
        show_MatchesBT = interactions.Button(
            style=interactions.ButtonStyle.SECONDARY,
            label="Show Matches",
            custom_id="show_matches",
            disabled=False
        )
        if (db.is_Owner(user_id)):
            create_matchBT = interactions.Button(
                style=interactions.ButtonStyle.SECONDARY,
                label="Create Match",
                custom_id="selectDayForMatch"
            )        
            row = interactions.ActionRow(components = [main_TeamBT, show_TeamsBT, create_matchBT, show_MatchesBT]) 
        else:
            row = interactions.ActionRow(components = [main_TeamBT, show_TeamsBT, show_MatchesBT]) 
        await ctx.defer(edit_origin=True)
        await ctx.edit("Team Commands:", embeds = [], components=row)

    @interactions.extension_component("home_button")
    async def home(self, ctx):
        await self.home_button(ctx)

    #Create Team 
    @interactions.extension_component("create_t")
    async def create_team(self, ctx):
        teamNameInput = interactions.TextInput(
            style=interactions.TextStyleType.SHORT,
            label="Enter a name for your scrim team:",
            custom_id="text_input_response",
            min_length=1,
            max_length=20,
        )
        modalTeamInput = interactions.Modal(
            title="Team Name",
            custom_id="db_create_team",
            components=[teamNameInput],
        )
        action_stack.append(ctx)
        await ctx.popup(modalTeamInput)

    #Create Match
    @interactions.extension_component("selectDayForMatch")
    async def selectDayForMatch(self, ctx):
        dt_list = []
        dateList = [(datetime.datetime.now() + datetime.timedelta(days=x)).date() for x in [0, 1, 2, 3, 4, 5, 6]]        
        for date in dateList:
            Soption = interactions.SelectOption(
                label=date.strftime("%m/%d/%Y"),
                value=date.strftime("%m/%d/%Y"),
                description=" ",
            )
            dt_list.append(Soption)        
        SMenu = interactions.SelectMenu(
            options=dt_list,
            placeholder="Day",
            custom_id="selectHourForMatch",
        )        
        await ctx.defer(edit_origin=True)
        await ctx.edit(" ", components=[SMenu])            

    #Create Match
    @interactions.extension_component("selectHourForMatch")
    async def selectHourForMatch(self, ctx, response : str):
        t_list = []
        timeList = ["17:00", "18:00", "19:00", "20:00", "21:00", "22:00"]        
        for time in timeList:
            Soption = interactions.SelectOption(
                label=time,
                value=response[0] + "_" + time,
                description=" ",
            )
            t_list.append(Soption)        
        SMenu = interactions.SelectMenu(
            options=t_list,
            placeholder="Hour",
            custom_id="db_create_match",
        )        
        await ctx.defer(edit_origin=True)
        await ctx.edit(" ", components=[SMenu])            

    @interactions.extension_component("db_create_match")
    async def db_create_match(self, ctx, response: str):
        date_split = response[0].split("_")
        year = date_split[0].split("/")[2]
        month= date_split[0].split("/")[1]
        day = date_split[0].split("/")[0]
        time_split = date_split[1].split(":")
        hour = time_split[0]
        minutes = time_split[1]
        dateTimeObj = datetime.datetime(int(year), int(month), int(day), int(hour), int(minutes), 0)
        author_id = int(ctx.author._json['user']['id'])
        team_obj = db.getTeamByOwnerID(author_id)['team']
        db.create_match(team_obj['_id'], dateTimeObj)
        embed, row = db.get_Team_Embed_Buttons(team_obj['_id'], author_id)
        await ctx.defer(edit_origin=True)
        await ctx.edit(embeds=[embed], components=row)

    @interactions.extension_modal("db_create_team")
    async def db_create_team(self, ctx, response: str):
        user_id = int(ctx.author._json['user']['id'])
        db_response = db.create_team(ctx.author, response)
        embed, row = db.get_Team_Embed_Buttons(db_response['_id'], user_id)
        #await ctx.send("Successful team creation", ephemeral=True)
        message = await ctx.send("Successful team creation", ephemeral=False)
        # can be deleted but then a none ephemeral message is pushed
        await message.delete()
        await action_stack[0].defer(edit_origin=True)
        await action_stack[0].edit(embeds=[embed], components=row)

    #Show all Teams
    @interactions.extension_component("show_teams")
    async def show_teams(self, ctx):
        teamObjects = db.get_all_teams()
        user_id = int(ctx.author._json['user']['id'])
        embeds = []
        row = []
        TeamOptionList = []
        for t in teamObjects:
            invited = False
            if user_id in t['invitation_ids']:
                invited = True
            Soption = interactions.SelectOption(
                label=str(t['name']),
                value=str(t['_id']),
                description=str(invitationMap[invited]),
            )
            TeamOptionList.append(Soption)
        if(TeamOptionList):
            SMenu = interactions.SelectMenu(
                options=TeamOptionList,
                placeholder="List of Teams",
                custom_id="showTeamWithID",
            )   
            await ctx.defer(edit_origin=True)
            await ctx.edit("", embeds=[], components=[SMenu])

    #Show all Matches
    @interactions.extension_component("show_matches")
    async def show_matches(self, ctx):
        matchObjects = db.get_all_matches()
        user_id = int(ctx.author._json['user']['id'])
        embeds = []
        row = []
        TeamOptionList = []
        for m in matchObjects:
            invited = False
            if user_id in m['roster1'] or user_id in m['roster2']:
                invited = True
            partofLabel = str("Entered") if invited else str(" ")
            team1 = str("Open Spot") if (m['team1'] == None) else db.getTeamByTeamID(m['team1'])['name']
            team2 = str("Open Spot") if (m['team2'] == None) else db.getTeamByTeamID(m['team2'])['name']
            label = team1 + str("vs.") + team2
            Soption = interactions.SelectOption(
                label=label,
                value=str(m['_id']),
                description=partofLabel,
            )
            TeamOptionList.append(Soption)
        if(TeamOptionList):
            SMenu = interactions.SelectMenu(
                options=TeamOptionList,
                placeholder="List of Scrims",
                custom_id="showMatchWithID",
            )   
            await ctx.defer(edit_origin=True)
            await ctx.edit("", embeds=[], components=[SMenu])

    #show the team with the given id
    @interactions.extension_component("showMatchWithID")
    async def showMatchWithID(self, ctx, response: str):
        # embed showing the current team
        match_id = str(response[0])
        user_id = int(ctx.author._json['user']['id'])
        team_Obj = db.getMatchbyMatchID(ObjectId(match_id))        
        embed, row = db.get_Match_Embed_Buttons(team_Obj['_id'], user_id)
        await ctx.defer(edit_origin=True)
        await ctx.edit(embeds=[embed], components=row)

    #show the team with the given id
    @interactions.extension_component("showTeamWithID")
    async def showTeamWithID(self, ctx, response: str):
        # embed showing the current team
        team_id = str(response[0])
        user_id = int(ctx.author._json['user']['id'])
        team_Obj = db.getTeamByTeamID(ObjectId(team_id))        
        embed, row = db.get_Team_Embed_Buttons(team_Obj["_id"], user_id)
        await ctx.defer(edit_origin=True)
        await ctx.edit(embeds=[embed], components=row)

    #show the team of the current user
    @interactions.extension_component("show_myTeam")
    async def show_myTeam(self, ctx):
        # embed showing the current team
        user_id = int(ctx.author._json['user']['id'])
        db_response = db.getTeamByOwnerID(user_id)
        embed, row = db.get_Team_Embed_Buttons(db_response["team"]["_id"], user_id)
        await ctx.defer(edit_origin=True)
        await ctx.edit(embeds=[embed], components=row)

    #Invite User
    @interactions.extension_component("invite_User")
    async def invite_User(self, ctx):
        userOptions = []
        author_id = int(ctx.author._json['user']['id'])
        team_id = db.getTeamByOwnerID(author_id)['team']['_id']
        UserCursor = db.get_all_validUsers(team_id)
        for user in UserCursor:
            Soption = interactions.SelectOption(
                label=str(user['discord_name']),
                value=int(user['discord_id']),
                description=str(user['summoner_name']),
            )
            userOptions.append(Soption)
        if(userOptions):
            SMenu = interactions.SelectMenu(
                options=userOptions,
                placeholder="Which user should be invited?",
                custom_id="db_invite_Player",
            )        
            await ctx.defer(edit_origin=True)
            await ctx.edit("", components=[SMenu])            
        else:
            await ctx.defer(edit_origin=True)
            await ctx.edit("Currently all users are either invited or already have a team.")

    #Db functions
    @interactions.extension_component("db_invite_Player")
    async def db_invite_Player(self, ctx, response: int):
        author_id = int(ctx.author._json['user']['id'])
        team_id = db.getTeamByOwnerID(author_id)['team']['_id']
        invitee_id = int(response[0])
        # require author_id, invitee_id, team_name
        db_response = db.invite_user(author_id, team_id, invitee_id)
        embed, row = db.get_Team_Embed_Buttons(team_id, author_id)
        await ctx.defer(edit_origin=True)
        await ctx.edit(embeds=[embed], components=row)

    #Leave Team    
    @interactions.extension_component("leave_Team")
    async def leave_team(self, ctx):
        user_id = int(ctx.author._json['user']['id'])
        team = db.getTeamByMemberID(user_id)
        if(team['status'] != "no_team"):
            db.leave_team(user_id, team["team"]["_id"])
            embed, row = db.get_Team_Embed_Buttons(team["team"]["_id"], user_id)            
            await ctx.defer(edit_origin=True)
            await ctx.edit(embeds=[embed], components=row)
        else:
            await ctx.defer(edit_origin=True)
            await ctx.edit("You are currently not part of a team.")

    #Join Team
    @interactions.extension_component("join_Team")
    async def join_team(self, ctx):
        user_id = int(ctx.author._json['user']['id'])
        teamNameInfo = ctx._json['message']['embeds'][0]['description']
        teamName = teamNameInfo.split("(")[1][:-1]
        team = db.getTeamByTeamName(str(teamName))
        if(team):
            db.join_team(user_id, team["_id"])
            embed, row = db.get_Team_Embed_Buttons(team["_id"], user_id)
            await ctx.defer(edit_origin=True)
            await ctx.edit(embeds=[embed], components=row)
        else:
            await ctx.defer(edit_origin=True)
            await ctx.edit("Something went wrong.")

    @interactions.extension_component("join_Match")
    async def join_match(self, ctx):
        #we can only reach this part of code, if the given match has two teams that have joined
        #what if one team leaves and rejoins? should the set of possible users stay stored for this specific combination? 
        #currently not considered
        user_id = int(ctx.author._json['user']['id'])
        teamNameInfo = ctx._json['message']['embeds'][0]['description']
        teamNames = teamNameInfo.split("(")[1]
        team1Name = teamNames.split("-")[0]
        #cut out last element ")"
        team2Name = teamNames.split("-")[1][0:-2]
        #find scrim match with the two given team names
        team1_id = db.getTeamByTeamName(team1Name)['_id']
        team2_id = db.getTeamByTeamNAme(team2Name)['_id']
        match_id = db.getMatchByTeams(team1_id, team2_id)['_id']
        result = db.join_match_asPlayer(user_id, match_id)
        #what is displayed the same as before so we want to get the embed as bevore in joni team
        embed, row = db.get_Match_Embed_Buttons(match_id, user_id)
        await ctx.defer(edit_origin=True)
        await ctx.edit(embeds=[embed], components=row)

    #Delete Team
    @interactions.extension_component("delete_Team")
    async def delete_team(self, ctx):
        author_id = int(ctx.author._json['user']['id'])
        team_id = db.getTeamByOwnerID(author_id)['team']['_id']
        db_response = db.remove_team(author_id, team_id)
        user_id = int(ctx.author._json['user']['id'])
        if (not db.has_Team(user_id)):
            main_TeamBT = interactions.Button(
                style=interactions.ButtonStyle.SECONDARY,
                label="Create Team",
                custom_id="create_t"
            )
        else:
            main_TeamBT = interactions.Button(
                style=interactions.ButtonStyle.SECONDARY,
                label="Team Hub",
                custom_id="show_myTeam"
            )
        existTeams = len(db.get_all_teams()) > 0
        show_TeamsBT = interactions.Button(
            style=interactions.ButtonStyle.SECONDARY,
            label="Show Teams",
            custom_id="show_teams",
            disabled=existTeams
        )
        show_MatchesBT = interactions.Button(
            style=interactions.ButtonStyle.SECONDARY,
            label="Show Matches",
            custom_id="show_matches",
            disabled=False
        )
        if (db.is_Owner(user_id)):
            create_matchBT = interactions.Button(
                style=interactions.ButtonStyle.SECONDARY,
                label="Create Match",
                custom_id="selectDayForMatch"
            )        
            row = interactions.ActionRow(components = [main_TeamBT, show_TeamsBT, create_matchBT, show_MatchesBT]) 
        else:
            row = interactions.ActionRow(components = [main_TeamBT, show_TeamsBT, show_MatchesBT]) 
        await ctx.defer(edit_origin=True)
        await ctx.edit("Team Commands:", embeds=[], components=row)


def setup(client):
    TeamCommands(client)
