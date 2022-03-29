import discord
from discord.ext import commands
import scrimdb as db
import logging
from datetime import datetime

# brainstorm 
# match structure
# datetime object
# team #1
# roster 1
# team #2
# roster 2


class MatchCommands(commands.Cog, name="MatchCommands"):
    def __init__(self, bot):
        self.bot = bot
        self.index = 0

    @commands.Cog.listener()
    async def on_ready(self):
        logging.info("Match commands loaded")


    @commands.command(name="match_create",
                      usage="<TeamName>")
    async def match_create(self, ctx, team_name, datetimeInp):
        # match_create team_name, day/month hour:minutes
        datetime_split = datetimeInp.split(" ")
        date = datetime_split[0]
        time = datetime_split[1]
        date_split = date.split("/")
        time_split = time.split(":")
        dt = datetime.datetime(2022, date_split[1], date_split[0], time_split[0], time_split[1])
        print(dt)
        result = db.create_match(ctx.author, arg)
        status = result['status']

        send_msg = ""
        if status == "created":
            send_msg = f"Your League team '{arg}' has been created.\n"
        elif status == "not_verified":
            send_msg = f"You have to link your league account before creating a team '!link <SummonerName>'.\n"
        elif status == "exists":
            send_msg = f"A team with this name does already exist.\n"
        await ctx.author.send(send_msg)        

    @commands.command(name="team_create",
                      usage="<TeamName>")
    async def match_show_all(self, ctx, arg):
        result = db.get_all_matches(ctx.author, arg)
        status = result['status']

        send_msg = ""
        if status == "created":
            send_msg = f"Your League team '{arg}' has been created.\n"
        elif status == "not_verified":
            send_msg = f"You have to link your league account before creating a team '!link <SummonerName>'.\n"
        elif status == "exists":
            send_msg = f"A team with this name does already exist.\n"
        await ctx.author.send(send_msg)       

    @commands.command(name="team_create",
                      usage="<TeamName>")
    async def match_show(self, ctx, arg):
        result = db.get_match(ctx.author, arg)
        status = result['status']

        send_msg = ""
        if status == "created":
            send_msg = f"Your League team '{arg}' has been created.\n"
        elif status == "not_verified":
            send_msg = f"You have to link your league account before creating a team '!link <SummonerName>'.\n"
        elif status == "exists":
            send_msg = f"A team with this name does already exist.\n"
        await ctx.author.send(send_msg)    

    @commands.command(name="team_create",
                      usage="<TeamName>")
    async def match_join(self, ctx, arg):
        result = db.join_match(ctx.author, arg)
        status = result['status']

        send_msg = ""
        if status == "created":
            send_msg = f"Your League team '{arg}' has been created.\n"
        elif status == "not_verified":
            send_msg = f"You have to link your league account before creating a team '!link <SummonerName>'.\n"
        elif status == "exists":
            send_msg = f"A team with this name does already exist.\n"
        await ctx.author.send(send_msg)    

    async def update_roster(self, ctx, match, team_nr, roster)
        print("update roster")

####Error Handling


            
def setup(bot):
    bot.add_cog(MatchCommands(bot))