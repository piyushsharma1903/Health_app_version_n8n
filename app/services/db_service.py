from pymongo import MongoClient
from app.config import settings

client = MongoClient(settings.MONGO_URI)
db = client[settings.MONGO_DB]
collection = db[settings.MONGO_COLLECTION]

def save_report(data: dict):
    """Insert lab report into MongoDB"""
    result = collection.insert_one(data)
    return str(result.inserted_id)
