import discord
from discord.ext import commands
import scrimdb as db
import logging

class MatchCommands(commands.Cog, name="MatchCommands"):
    def __init__(self, bot):
        self.bot = bot
        self.index = 0

    @commands.Cog.listener()
    async def on_ready(self):
        logging.info("Match commands loaded")


    @commands.command(name="team_create",
                      usage="<TeamName>")
    async def match_create(self, ctx, arg):
        result = db.create_team(ctx.author, arg)
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
        result = db.create_team(ctx.author, arg)
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
        result = db.create_team(ctx.author, arg)
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
        result = db.create_team(ctx.author, arg)
        status = result['status']

        send_msg = ""
        if status == "created":
            send_msg = f"Your League team '{arg}' has been created.\n"
        elif status == "not_verified":
            send_msg = f"You have to link your league account before creating a team '!link <SummonerName>'.\n"
        elif status == "exists":
            send_msg = f"A team with this name does already exist.\n"
        await ctx.author.send(send_msg)    


####Error Handling


            
def setup(bot):
    bot.add_cog(MatchCommands(bot))