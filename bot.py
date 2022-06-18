# bot.py
import os
import discord
from discord.ext.commands import Bot
from discord.ext import commands
from dotenv import load_dotenv
import asyncio
import sys
import logging
logging.basicConfig(filename='System.log', level=logging.DEBUG)

import interactions

from Cogs.TeamCommands import TeamCommands

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




bot.load('Cogs.MainUtility')
bot.load('Cogs.TeamCommands')

bot.start() 



