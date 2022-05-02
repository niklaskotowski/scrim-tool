import discord
from discord.ext import commands
import scrimdb as db
import logging
import interactions

# TODO:
# create a !team commands that shows additional functionality by displaying emojis and corresponding functions 
# emoji1 -> team create
# emoji2 -> team show
# emoji3 -> when the function requires an argument, send a private message such that the user has to enter the argument he is asked for

# create an embed template to display teams
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


    @interactions.extension_command(
        name="team_overview",
        description="Displays a list of team commands",
        scope=271639846307627008,
    )
    async def team_overview(self, ctx):
        create_TeamBT = interactions.Button(
            style=interactions.ButtonStyle.SECONDARY,
            label="Create Team",
            custom_id="create_t"
        )
        show_TeamsBT = interactions.Button(
            style=interactions.ButtonStyle.SECONDARY,
            label="Show Teams",
            custom_id="show_teams"
        )
        row = interactions.ActionRow(components = [create_TeamBT, show_TeamsBT]) 
        await ctx.send("Team Commands:", components=row)

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

    # @commands.command(name="team_show")
    # async def team_show(self, ctx, arg1):
    #     # list team members
    #     # list avg elo
    #     # list w/l ratio
    #     db_response = db.get_team(ctx.author, arg1)
    #     logging.info(f"Team Show Response: {db_response}")
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
