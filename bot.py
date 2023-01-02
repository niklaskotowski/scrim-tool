# bot.py
import os
import discord
from discord.ext.commands import Bot
from discord.ext import commands
from dotenv import load_dotenv
import logging
logging.basicConfig(level=logging.DEBUG)

import interactions

from Cogs.TeamCommands import TeamCommands

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
help_command = commands.DefaultHelpCommand(
    no_category = 'Commands'
)
desc = "Manage your League of Legends Scrims with this application."

bot = interactions.Client(token=TOKEN)

bot.load('Cogs.TeamCommands')
bot.load('Cogs.UserCommands')

bot.start() 



