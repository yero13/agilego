from pymongo import MongoClient

client = MongoClient('mongodb://agilego:1@127.0.0.1:27017/')
db = client.agilego
