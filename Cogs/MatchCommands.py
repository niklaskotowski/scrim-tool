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
    async def match_create(self, ctx, team_name, date, time):
        # match_create team_name, day/month hour:minutes
        date_split = date.split("/")
        time_split = time.split(":")
        dt = datetime(2022, int(date_split[1]), int(date_split[0]), int(time_split[0]), int(time_split[1]))

        result = db.create_match(ctx.author, team_name, dt)
        status = result['status']

        send_msg = ""
        if status == "team_notfound":
            send_msg = f"The named team has not been found.\n"
        elif status == "not_owner":
            send_msg = f"Only the team owner is allowed to schedule a match.\n"
        elif status == "created":
            send_msg = f"A match has been scheduled to {dt}.\n"
        await ctx.author.send(send_msg)        

    @commands.command(name="match_show_all",
                      usage="<TeamName>")
    async def match_show_all(self, ctx):
        result = db.get_all_matches(ctx.author)
        status = result['status']

        send_msg = ""
        if status == "success":
            send_msg = f"Currently open matches:\n"
            embed=discord.Embed()
            embed.set_author(name="ScrimManager")
            embed.add_field(name="Time:", value=datetime.now().strftime("%Y-%m-%d %H:%M:%S"), inline=False)
            embed.add_field(name="Team 1:", value="OlsCs", inline=True)
            embed.add_field(name="Roster:", value="Secr3t\nVictoriousMuffin\nCpt Aw\n", inline=True)
            embed.add_field(name='\u200b', value='\u200b', inline=False)
            embed.add_field(name="Team 2:", value="OlsCock", inline=True)
            embed.add_field(name="Roster:", value="Diviine\nRalle\nGabi ", inline=True)
        await ctx.send(embed=embed)       

    @commands.command(name="match_show",
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

    @commands.command(name="match_join",
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

    async def update_roster(self, ctx, match, team_nr, roster):
        print("update roster")

####Error Handling


            
def setup(bot):
    bot.add_cog(MatchCommands(bot))