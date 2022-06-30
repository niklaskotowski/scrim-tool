from code import interact
from attr import field
import discord
from discord.ext import commands
import scrimdb as db
import logging
import interactions
from bson.objectid import ObjectId

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
        show_TeamsBT = interactions.Button(
            style=interactions.ButtonStyle.SECONDARY,
            label="Show Teams",
            custom_id="show_teams"
        )
        row = interactions.ActionRow(components = [main_TeamBT, show_TeamsBT]) 
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
        show_TeamsBT = interactions.Button(
            style=interactions.ButtonStyle.SECONDARY,
            label="Show Teams",
            custom_id="show_teams"
        )
        row = interactions.ActionRow(components = [main_TeamBT, show_TeamsBT])
        await ctx.defer(edit_origin=True)
        await ctx.edit("Team Commands:", components=row)

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
        show_TeamsBT = interactions.Button(
            style=interactions.ButtonStyle.SECONDARY,
            label="Show Teams",
            custom_id="show_teams"
        )
        action_stack.append(ctx)
        await ctx.popup(modalTeamInput)

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
            #,await ctx.defer(edit_origin=True)
            await ctx.send("", components=[SMenu])
        else:
            #await ctx.defer(edit_origin=True) 
            await ctx.send("Currently there are no teams.")

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

    #Delete Team
    @interactions.extension_component("delete_Team")
    async def delete_team(self, ctx):
        author_id = int(ctx.author._json['user']['id'])
        team_id = db.getTeamByOwnerID(author_id)['team']['_id']
        db_response = db.remove_team(author_id, team_id)
        
        #await ctx.edit(embeds=[], components=[])
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
        show_TeamsBT = interactions.Button(
            style=interactions.ButtonStyle.SECONDARY,
            label="Show Teams",
            custom_id="show_teams"
        )
        row = interactions.ActionRow(components = [main_TeamBT, show_TeamsBT])
        await ctx.defer(edit_origin=True)
        await ctx.edit("Team Commands:", embeds=[], components=row)


def setup(client):
    TeamCommands(client)
