from code import interact
from attr import field
import discord
from discord.ext import commands
import scrimdb as db
import logging
import interactions
from bson.objectid import ObjectId

# TODO:
# construct a standart obj of team infos and member infos which is returned by calling get_team
# then create functions which return bools for hasTeam and isOwner to display different buttons dependent on the current status

swords = "\u2694\uFE0F"
raised_hand = "\u270B"
exit = 	"\u274C"
check = "\u2705"

#0-> " ",1 -> Open Invitation
invitationMap = ['______________', 'Open Invitation']

class TeamCommands(interactions.Extension):
    def __init__(self, client):
        self.client: interactions.Client = client

    @commands.Cog.listener()
    async def on_ready(self):
        logging.info("Team Commands loaded")

    ####Team Overview CMD####
    @interactions.extension_command(
        name="team_overview",
        description="Displays a list of team commands",
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
        await ctx.send("Team Commands:", components=row, ephemeral=False)

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
        await ctx.popup(modalTeamInput)

    @interactions.extension_modal("db_create_team")
    async def db_create_team(self, ctx, response: str):
        user_id = int(ctx.author._json['user']['id'])
        db_response = db.create_team(ctx.author, response)
        embed, row = db.get_Team_Embed_Buttons(db_response['_id'], user_id)
        await ctx.send(embeds=[embed], components=row, ephemeral=True)

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
            await ctx.send("", components=[SMenu], ephemeral=True)
        else:
            await ctx.send("Currently there are not teams.", ephemeral=True)

    #show the team with the given id
    @interactions.extension_component("showTeamWithID")
    async def showTeamWithID(self, ctx, response: str):
        # embed showing the current team
        team_id = str(response[0])
        user_id = int(ctx.author._json['user']['id'])
        team_Obj = db.getTeamByTeamID(ObjectId(team_id))        
        embed, row = db.get_Team_Embed_Buttons(team_Obj["_id"], user_id)
        await ctx.send(embeds=[embed], components=row, ephemeral=True)

    #show the team of the current user
    @interactions.extension_component("show_myTeam")
    async def show_myTeam(self, ctx):
        # embed showing the current team
        user_id = int(ctx.author._json['user']['id'])
        db_response = db.getTeamByOwnerID(user_id)
        embed, row = db.get_Team_Embed_Buttons(db_response["team"]["_id"], user_id)
        await ctx.send(embeds=[embed], components=row, ephemeral=True)

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
            await ctx.send("", components=[SMenu], ephemeral=True)
        else:
            await ctx.send("Currently all users are either invited or already have a team.", ephemeral=True)

    #Db functions
    @interactions.extension_component("db_invite_Player")
    async def db_invite_Player(self, ctx, response: int):
        author_id = int(ctx.author._json['user']['id'])
        team_id = db.getTeamByOwnerID(author_id)['team']['_id']
        invitee_id = int(response[0])
        # require author_id, invitee_id, team_name
        db_response = db.invite_user(author_id, team_id, invitee_id)
        logging.info(f"Team Invite Response: {db_response}")
        await ctx.send(db_response.discord_msg(), ephemeral=True)

    #Leave Team    
    @interactions.extension_component("leave_Team")
    async def leave_team(self, ctx):
        user_id = int(ctx.author._json['user']['id'])
        team = db.getTeamByMemberID(user_id)
        if(team['status'] != "no_team"):
            db.leave_team(user_id, team["team"]["_id"])
            embed, row = db.get_Team_Embed_Buttons(team["team"]["_id"], user_id)
            await ctx.send(embeds=[embed], components=row, ephemeral=True)
        else:
            await ctx.send("You are currently not part of a team.", ephemeral=True)

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
            await ctx.send(embeds=[embed], components=row, ephemeral=True)
        else:
            await ctx.send("Something went wrong.", ephemeral=True)

    #Delete Team
    @interactions.extension_component("delete_Team")
    async def delete_team(self, ctx):
        author_id = int(ctx.author._json['user']['id'])
        team_id = db.getTeamByOwnerID(author_id)['team']['_id']
        db_response = db.remove_team(author_id, team_id)
        await ctx.send(db_response.discord_msg(), ephemeral=True)
            

        
    # @commands.command(name="team_join",
    #                   usage="<TeamName>")
    # async def team_join(self, ctx, arg1):
    #     db_response = db.join_team(ctx.author, arg1)
    #     logging.info(f"Team Join Response: {db_response}")
    #     await ctx.author.send(db_response.discord_msg())


    # @commands.command(name="team_list")
    # async def team_list(self, ctx):
    #     # list team all existing teams and their member count
    #     db_response = db.get_all_teams(ctx.author)
    #     logging.info(f"Team List Response: {db_response}")
    #     await ctx.author.send(db_response.discord_msg())

    # @team_create.error
    # async def team_create_error(self, ctx, error):
    #     if isinstance(error, discord.ext.commands.errors.MissingRequiredArgument):
    #         await ctx.author.send(f"Error: You need to provide a team name\nUsage: !team_create <TeamName>")

    # @team_invite.error
    # async def team_invite_error(self, ctx, error):
    #     if isinstance(error, discord.ext.commands.errors.MissingRequiredArgument):
    #         await ctx.author.send(
    #             f"Error: You need to provide a team name and specify a player\nUsage: !team_invite <TeamName> <PlayerName>")

    # @team_join.error
    # async def team_join_error(self, ctx, error):
    #     if isinstance(error, discord.ext.commands.errors.MissingRequiredArgument):
    #         await ctx.author.send(f"Error: You need to provide a team name\nUsage: !team_join <TeamName>")

    # @team_leave.error
    # async def team_leave_error(self, ctx, error):
    #     if isinstance(error, discord.ext.commands.errors.MissingRequiredArgument):
    #         await ctx.author.send(f"Error: You need to provide a team name\nUsage: !team_leave <TeamName>")

    # @team_delete.error
    # async def team_delete_error(self, ctx, error):
    #     if isinstance(error, discord.ext.commands.errors.MissingRequiredArgument):
    #         await ctx.author.send(f"Error: You need to provide a team name\nUsage: !team_delete <TeamName>")

    # @team_show.error
    # async def team_show_error(self, ctx, error):
    #     if isinstance(error, discord.ext.commands.errors.MissingRequiredArgument):
    #         await ctx.author.send(f"Error: You need to provide a team name\nUsage: !team_show <TeamName>")


def setup(client):
    TeamCommands(client)
