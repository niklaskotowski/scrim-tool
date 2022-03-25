# bot.py
import os
import discord
from discord.ext.commands import Bot
from discord.ext import commands
from dotenv import load_dotenv
import asyncio
import sys

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
help_command = commands.DefaultHelpCommand(
    no_category = 'Commands'
)
includes = ['Cogs.MainUtility', 'Cogs.TeamData', 'Cogs.UserCommands']
desc = "Manage your League of Legends Scrims with this application. Credits JohanLohr"

bot = Bot(command_prefix='!', description=desc, help_command=help_command)

# !link <SummonerName> - Verbinden von League Account -> UUID mit der man sich verifiziert
# Bei jedem Aufruf checken ob verified -> Ansonsten bescheid geben dass man das machen soll
# !team_create <Name> - Checken ob es schon vorhanden ist
# !team_invite <DiscordName>
# !team_join <TeamName>
# !team_Search
# !user_info



@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

if __name__ == '__main__':
    for include in includes:
        try:
            bot.load_extension(include)
        except Exception as e:
            print(e )
            print(f'Failed to load extension {include}', file=sys.stderr)

bot.run(TOKEN)

