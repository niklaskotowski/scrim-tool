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
        print(user_id)
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
        await ctx.send("Team Commands:", components=row, ephemeral=True)

    ####Create Team CMD####
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
        db_response = db.create_team(ctx.author, response)
        logging.info(f"Team Create Response: {db_response}")
        await ctx.author.send(db_response.discord_msg())

    ####Show all Teams CMD####
    @interactions.extension_component("show_teams")
    async def show_teams(self, ctx):
        db_response = db.get_all_teams()
        logging.info(f"Team List Response: {db_response}")
        await ctx.author.send(db_response.discord_msg())   

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

    ####SHOW MY_TEAM --- OF ANY TEAM####
    ####Invite User in Team CMD####    
    @interactions.extension_component("show_myTeam")
    async def show_myTeam(self, ctx):
        # embed showing the current team
        playerField = interactions.EmbedField(
            name="Member: ",
            value="[Max](https://euw.op.gg/summoners/euw/Secr3t)\nMoritz\nMartin\nOl\nRalf",
            inline=True,
        )
        statisticsField = interactions.EmbedField(
            name="Statistics: ",
            value='Wins: 2, Defeats: 0',
            inline=True,
        )
        embed=interactions.Embed(title=" ", color=2, description="Team Hub (Fish of the Sea)", fields=[playerField, statisticsField])
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
        if (db.is_Owner(user_id)):
            buttons = [invite_MemberBT, leave_TeamBT, deleteTeamBT]
        else:
            buttons = [leave_TeamBT]
        row = interactions.ActionRow(components = buttons) 
        await ctx.send(embeds=[embed], components=row, ephemeral=True)


    @interactions.extension_component("invite_User")
    async def invite_User(self, ctx):
        userOptions = []
        UserCursor = db.get_all_Users()
        for user in UserCursor:
            Soption = interactions.SelectOption(
                label=str(user['discord_name']),
                value=int(user['discord_id']),
                description=str(user['summoner_name']),
            )
            userOptions.append(Soption)

        SMenu = interactions.SelectMenu(
            options=userOptions,
            placeholder="Which user should be invited?",
            custom_id="db_invite_Player",
        )
        # playerNameInput = interactions.TextInput(
        #     style=interactions.TextStyleType.SHORT,
        #     label="Enter a player name",
        #     custom_id="text_input_response",
        #     min_length=1,
        #     max_length=20,
        # )
        # modalPlayerInput = interactions.Modal(
        #     title="Player Name",
        #     custom_id="db_invite_Player",
        #     components=[playerNameInput],
        # )
        # await ctx.popup(modalPlayerInput)
        await ctx.send("", components=[SMenu], ephemeral=True)

    @interactions.extension_component("db_invite_Player")
    async def db_invite_Player(self, ctx, response: int):
        author_id = int(ctx.author._json['user']['id'])
        team_id = db.getTeamByOwnerID(author_id)['team']['_id']
        invitee_id = int(response[0])
        # require author_id, invitee_id, team_name
        db_response = db.invite_user(author_id, team_id, invitee_id)
        logging.info(f"Team Invite Response: {db_response}")
        await ctx.author.send(db_response.discord_msg())

    # @commands.command(name="team_invite",
    #                   usage="<TeamName> <PlayerName>")
    # async def team_invite(self, ctx, arg1, user: discord.Member = None):
    #     db_response = db.invite_user(ctx.author, arg1, user)
    #     logging.info(f"Team Invite Response: {db_response}")
    #     await ctx.author.send(db_response.discord_msg())
        
    # @commands.command(name="team_join",
    #                   usage="<TeamName>")
    # async def team_join(self, ctx, arg1):
    #     db_response = db.join_team(ctx.author, arg1)
    #     logging.info(f"Team Join Response: {db_response}")
    #     await ctx.author.send(db_response.discord_msg())

    # @commands.command(name="team_leave")
    # async def team_leave(self, ctx, arg1):
    #     db_response = db.leave_team(ctx.author, arg1)
    #     logging.info(f"Team Leave Response: {db_response}")
    #     await ctx.author.send(db_response.discord_msg())

    # @commands.command(name="team_delete")
    # async def team_delete(self, ctx, arg1):
    #     db_response = db.remove_team(ctx.author, arg1)
    #     logging.info(f"Team Delete Response: {db_response}")
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
