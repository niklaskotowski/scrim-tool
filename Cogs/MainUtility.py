import discord
from discord.ext import commands
import scrimdb as db
import interactions

class MainUtility(interactions.Extension):
    def __init__(self, client):
        self.client: interactions.Client = client

def setup(client):
    MainUtility(client)


