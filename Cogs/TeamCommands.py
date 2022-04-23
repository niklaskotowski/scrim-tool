import discord
from discord.ext import commands
import scrimdb as db
import logging

# TODO:
# create a !team commands that shows additional functionality by displaying emojis and corresponding functions 
# emoji1 -> team create
# emoji2 -> team show
# emoji3 -> when the function requires an argument, send a private message such that the user has to enter the argument he is asked for

# create an embed template to display teams

class TeamCommands(commands.Cog, name="TeamCommands"):
    def __init__(self, bot):
        self.bot = bot
        self.index = 0

    @commands.Cog.listener()
    async def on_ready(self):
        logging.info("Team Commands loaded")

    @commands.command(name="team_create",
                      usage="<TeamName>")
    async def team_create(self, ctx, arg):
        db_response = db.create_team(ctx.author, arg)
        logging.info(f"Team Create Response: {db_response}")
        await ctx.author.send(db_response.discord_msg())

    @commands.command(name="team_invite",
                      usage="<TeamName> <PlayerName>")
    async def team_invite(self, ctx, arg1, user: discord.Member = None):
        db_response = db.invite_user(ctx.author, arg1, user)
        logging.info(f"Team Invite Response: {db_response}")
        await ctx.author.send(db_response.discord_msg())
        
    @commands.command(name="team_join",
                      usage="<TeamName>")
    async def team_join(self, ctx, arg1):
        db_response = db.join_team(ctx.author, arg1)
        logging.info(f"Team Join Response: {db_response}")
        await ctx.author.send(db_response.discord_msg())

    @commands.command(name="team_leave")
    async def team_leave(self, ctx, arg1):
        db_response = db.leave_team(ctx.author, arg1)
        logging.info(f"Team Leave Response: {db_response}")
        await ctx.author.send(db_response.discord_msg())

    @commands.command(name="team_delete")
    async def team_delete(self, ctx, arg1):
        db_response = db.remove_team(ctx.author, arg1)
        logging.info(f"Team Delete Response: {db_response}")
        await ctx.author.send(db_response.discord_msg())

    @commands.command(name="team_show")
    async def team_show(self, ctx, arg1):
        # list team members
        # list avg elo
        # list w/l ratio
        db_response = db.get_team(ctx.author, arg1)
        logging.info(f"Team Show Response: {db_response}")
        await ctx.author.send(db_response.discord_msg())

    @commands.command(name="team_list")
    async def team_list(self, ctx):
        # list team all existing teams and their member count
        db_response = db.get_all_teams(ctx.author)
        logging.info(f"Team List Response: {db_response}")
        await ctx.author.send(db_response.discord_msg())

    @team_create.error
    async def team_create_error(self, ctx, error):
        if isinstance(error, discord.ext.commands.errors.MissingRequiredArgument):
            await ctx.author.send(f"Error: You need to provide a team name\nUsage: !team_create <TeamName>")

    @team_invite.error
    async def team_invite_error(self, ctx, error):
        if isinstance(error, discord.ext.commands.errors.MissingRequiredArgument):
            await ctx.author.send(
                f"Error: You need to provide a team name and specify a player\nUsage: !team_invite <TeamName> <PlayerName>")

    @team_join.error
    async def team_join_error(self, ctx, error):
        if isinstance(error, discord.ext.commands.errors.MissingRequiredArgument):
            await ctx.author.send(f"Error: You need to provide a team name\nUsage: !team_join <TeamName>")

    @team_leave.error
    async def team_leave_error(self, ctx, error):
        if isinstance(error, discord.ext.commands.errors.MissingRequiredArgument):
            await ctx.author.send(f"Error: You need to provide a team name\nUsage: !team_leave <TeamName>")

    @team_delete.error
    async def team_delete_error(self, ctx, error):
        if isinstance(error, discord.ext.commands.errors.MissingRequiredArgument):
            await ctx.author.send(f"Error: You need to provide a team name\nUsage: !team_delete <TeamName>")

    @team_show.error
    async def team_show_error(self, ctx, error):
        if isinstance(error, discord.ext.commands.errors.MissingRequiredArgument):
            await ctx.author.send(f"Error: You need to provide a team name\nUsage: !team_show <TeamName>")


def setup(bot):
    bot.add_cog(TeamCommands(bot))
