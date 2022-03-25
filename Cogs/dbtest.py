from pymongo import MongoClient
from dotenv import load_dotenv
import os
from random import randint
#Step 1: Connect to MongoDB - Note: Change connection string as needed

load_dotenv()
client = MongoClient(os.getenv('MONGO_URI'))


db = client['scrimdb']
collection = db.users
playerObject = {'name': "Test", 'elo_soloq': "Iron", 'elo_flexq': "Bronze"}
result = collection.insert_one(playerObject)


print('finished creating playerObject')

client.close()