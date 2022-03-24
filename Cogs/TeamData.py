import discord
from discord.ext import commands


class MainUtility(commands.Cog, name="MainClass"):
    def __init__(self, bot):
        self.bot = bot
        self.index = 0

    @commands.Cog.listener()
    async def on_ready(self):
        print("Log:", self.bot.user)


def setup(bot):
    bot.add_cog(MainUtility(bot))
    print("Log: TeamData is loaded.")