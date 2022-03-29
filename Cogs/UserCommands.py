import discord
from discord.ext import commands
import scrimdb as db
import message_helper as msg
import logging


class UserCommands(commands.Cog, name="UserCommands"):
    def __init__(self, bot):
        self.bot = bot
        self.index = 0

    @commands.Cog.listener()
    async def on_ready(self):
        logging.info("User Commands loaded")

    @commands.command(name="unlink")
    async def unlink(self, ctx):
        dels = db.unlink_command(ctx.author)
        await ctx.author.send(f"Removed Links: {dels}")

    @commands.command(name="link",
                      usage="<LeagueName>")
    async def link(self, ctx, arg):
        result = db.link_command(arg, ctx.author)
        logging.debug(f"Link Call Response: {result}")
        status = result['status']

        if status == "created":
            send_msg = f"Your Discord account has been linked to Summoner '{result['summoner_name']}'.\n" \
                   f"To verify that this account belong to you please enter the following code:\n" \
                   f"{result['verify']}\n" \
                   f"You can enter this code in the League of Legends settings under 'Verification'."
            await ctx.author.send(send_msg)

        if status == "verified":
            await ctx.author.send(f"You have already verified Summoner '{result['summoner_name']}'\n"
                                  f"Use !unlink to remove all verifications for this Discord User.")

        if status == "rejected":
            await ctx.author.send(f"Summoner '{result['summoner_name']}' has already been verified by another user.")

        if status == "invalid":
            await ctx.author.send(f"Summoner '{result['summoner_name']}' does not exist on EUW.")

    @link.error
    async def link_error(self, ctx, error):
        if isinstance(error, discord.ext.commands.errors.MissingRequiredArgument):
            await ctx.author.send(f"Error: You need to provide your League Summoner Name\nUsage: !link <SummonerName>")

    @commands.command(name="rankedinfo")
    async def rankedinfo(self, ctx):
        result = db.rankedinfo_command(ctx.author)
        status = result['status']

        if status == "success":
            await ctx.author.send(msg.command_rankedinfo(result['data']))





def setup(bot):
    bot.add_cog(UserCommands(bot))