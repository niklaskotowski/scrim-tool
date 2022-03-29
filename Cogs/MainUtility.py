import discord
from discord.ext import commands
import scrimdb as db

class MainUtility(commands.Cog, name="MainClass"):
    def __init__(self, bot):
        self.bot = bot
        self.index = 0

    @commands.Cog.listener()
    async def on_ready(self):
        print("Log:", self.bot.user)

    @commands.command(name="hw")
    async def hw(self, ctx):
        print("Hello Schwanz.")
        await ctx.author.send("BASTARD")


def setup(bot):
    bot.add_cog(MainUtility(bot))
    print("Log: Main is loaded.")
