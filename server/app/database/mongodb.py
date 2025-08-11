from pymongo import MongoClient
from pymongo.synchronous.collection import Collection

from app.core.config import settings

mg_client = MongoClient(settings.MONGO_URI)

def get_mongo_collection(collection_name: str) -> Collection:
    """
    Get a MongoDB collection.

    Args:
        collection_name (str): The name of the collection to retrieve.

    Returns:
        Collection: The MongoDB collection object.
    """
    db = mg_client["chat_history"]
    return db[collection_name]
