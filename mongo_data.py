
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

uri = "mongodb://andyblake:crs19981106@undefined/?replicaSet=atlas-8yp836-shard-0&ssl=true&authSource=admin"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)