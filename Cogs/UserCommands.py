import discord
from discord.ext import commands
import scrimdb as db
import message_helper as msg
import logging


class UserCommands(commands.Cog, name="UserCommands"):
    def __init__(self, bot):
        self.bot = bot
        self.index = 0

    @commands.command(name="unlink")
    async def unlink(self, ctx):
        dels = db.unlink_command(ctx.author)
        await ctx.author.send(f"Removed Links: {dels}")

    @commands.command(name="link",
                      usage="<LeagueName>")
    async def link(self, ctx, arg):
        db_response = db.link_command(arg, ctx.author)
        await ctx.author.send(db_response.discord_msg())

    @link.error
    async def link_error(self, ctx, error):
        if isinstance(error, discord.ext.commands.errors.MissingRequiredArgument):
            await ctx.author.send(f"Error: You need to provide your League Summoner Name\nUsage: !link <SummonerName>")

    @commands.command(name="rankedinfo")
    async def rankedinfo(self, ctx):
        db_response = db.rankedinfo_command(ctx.author)
        await ctx.author.send(db_response.discord_msg())





def setup(bot):
    bot.add_cog(UserCommands(bot))