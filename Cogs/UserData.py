from pymongo import MongoClient
from random import randint
#Step 1: Connect to MongoDB - Note: Change connection string as needed

db = client['playerbase']
#Step 2: Create sample data
name = 'Diviine'
eloSQ = 'Silver'
eloFQ = 'Gold'
collection = db.playerbase
playerObject = {'name': name, 'elo_soloq': eloSQ, 'elo_flexq': eloFQ}


result = collection.insert_one(playerObject)

print('finished creating playerObject', name)
