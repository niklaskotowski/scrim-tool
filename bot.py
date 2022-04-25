# bot.py
import os
import discord
from discord.ext.commands import Bot
from discord.ext import commands
from dotenv import load_dotenv
import asyncio
import sys
import logging
import interactions

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
help_command = commands.DefaultHelpCommand(
    no_category = 'Commands'
)
includes = ['Cogs.MainUtility', 'Cogs.UserCommands', 'Cogs.TeamCommands', 'Cogs.MatchCommands']
desc = "Manage your League of Legends Scrims with this application."

#bot = Bot(command_prefix='!', description=desc, help_command=help_command)

# !link <SummonerName> - Verbinden von League Account -> UUID mit der man sich verifiziert
# Bei jedem Aufruf checken ob verified -> Ansonsten bescheid geben dass man das machen soll
# !team_create <Name> - Checken ob es schon vorhanden ist
# !team_invite <DiscordName>
# !team_join <TeamName>
# !team_Search
# !user_info
bot = interactions.Client(token=TOKEN)

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [%(name)s] [%(levelname)s] - %(message)s',
                    datefmt='%m/%d/%Y %H:%M:%S',
                    handlers=[
                        logging.FileHandler("scrimdb.log"),
                        logging.StreamHandler()
                    ])


@bot.event
async def on_ready():
    print(f' has connected to Discord!')


@bot.command(name="team_overview",
            description="command test")
async def team_overview(ctx: interactions.CommandContext):
    # no database access requiered for this operation    
    button = interactions.Button(
        style=interactions.ButtonStyle.PRIMARY,
        label="hello world!",
        custom_id="hello"
    )
    await ctx.send("testing", components=button)

bot.start() 

# if __name__ == '__main__':
#     for include in includes:
#         try:
#             bot.load_extension(include)
#         except Exception as e:
#             print(e )
#             print(f'Failed to load extension {include}', file=sys.stderr)



