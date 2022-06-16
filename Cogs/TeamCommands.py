from code import interact
from attr import field
import discord
from discord.ext import commands
import scrimdb as db
import logging
import interactions

# TODO:
# construct a standart obj of team infos and member infos which is returned by calling get_team
# then create functions which return bools for hasTeam and isOwner to display different buttons dependent on the current status

swords = "\u2694\uFE0F"
raised_hand = "\u270B"
exit = 	"\u274C"
check = "\u2705"

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
        embed = db.get_Team_Embed(db_response['_id'])
        embed, row = db.get_Team_Embed_Buttons(db_response['_id'], user_id)
        await ctx.send(embeds=[embed], components=row, ephemeral=False)

    #Show all Teams
    @interactions.extension_component("show_teams")
    async def show_teams(self, ctx):
        db_response = db.get_all_teams()
        logging.info(f"Team List Response: {db_response}")
        await ctx.send(db_response.discord_msg(), ephemeral=False)   

    # ####Show specified Team CMD####
    # @interactions.extension_component("show_t")
    # async def show_t(self, ctx):
    #     teamNameInput = interactions.TextInput(
    #         style=interactions.TextStyleType.SHORT,
    #         label="Enter the name of the team:",
    #         custom_id="text_input_response",
    #         min_length=1,
    #         max_length=20,
    #     )
    #     modalTeamInput = interactions.Modal(
    #         title="Team Name",
    #         custom_id="db_get_team",
    #         components=[teamNameInput],
    #     )
    #     await ctx.popup(modalTeamInput)

    # @interactions.extension_modal("db_get_team")
    # async def db_get_team(self, ctx, response:str):
    #     # list team members
    #     # list avg elo
    #     # list w/l ratio
    #     db_response = db.get_team(ctx.author, response)
    #     logging.info(f"Team Show Response: {db_response}")
    #     await ctx.author.send(db_response.discord_msg())

    #show the team of the current user
    @interactions.extension_component("show_myTeam")
    async def show_myTeam(self, ctx):
        # embed showing the current team
        db_response = db.getTeamByOwnerID(int(ctx.author._json['user']['id']))
        teamInfo = db_response['team']
        member_ids = [x for x in teamInfo['member_ids']]
        db_response = db.getUsersByIDs(member_ids)
        user_Objects = db_response['userObjects']
        member_list = ["[" + str(x['discord_name'].split("#")[0]) + "]" + "(https://euw.op.gg/summoners/euw/" + str(x['summoner_name']) + ")\n" for x in user_Objects]
        member_string = "".join(member_list)
        if(member_string == ""):
            member_string = "Currently empty"
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
        embed=interactions.Embed(title=" ", color=2, description="Team Hub (" + teamInfo['name'] + ")", fields=[playerField, statisticsField])
        user_id = int(ctx.author._json['user']['id'])

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
        deleteTeamBT = interactions.Button(
            style=interactions.ButtonStyle.SECONDARY,
            label="Delete",
            custom_id="delete_Team"
        )
        if (db.is_Owner(user_id) and db.isPartofATeam(user_id)):
            buttons = [invite_MemberBT, leave_TeamBT, deleteTeamBT]
        elif(db.is_Owner(user_id) and not db.isPartofATeam(user_id)):
            buttons = [invite_MemberBT, deleteTeamBT]
        elif(db.isPartofATeam(user_id) and not db.is_Owner(user_id)):
            buttons = [leave_TeamBT]
        else:
            buttons = []
        row = interactions.ActionRow(components = buttons) 
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
            db_response = db.leave_team(user_id, team["team"]["_id"])
            embed, row = db.get_Team_Embed_Buttons(team["team"]["_id"], user_id)
            await ctx.send(embeds=[embed], components=row, ephemeral=False)
        else:
            await ctx.send("You are currently not part of a team.", ephemeral=True)


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
