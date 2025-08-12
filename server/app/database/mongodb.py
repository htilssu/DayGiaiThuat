from bson import ObjectId
from pydantic import GetCoreSchemaHandler, GetJsonSchemaHandler
from pydantic_core import core_schema
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


class PyObjectId(str):
    @classmethod
    def __get_pydantic_core_schema__(cls, _source_type, _handler: GetCoreSchemaHandler) -> core_schema.CoreSchema:
        return core_schema.no_info_plain_validator_function(cls.validate)

    @classmethod
    def validate(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        if isinstance(v, str):
            return v
        raise TypeError("Invalid ObjectId type")

    @classmethod
    def __get_pydantic_json_schema__(cls, _core_schema, handler: GetJsonSchemaHandler):
        json_schema = handler(core_schema.str_schema())
        json_schema.update(type="string", examples=["64b0c0f2f2a4f2c1a5d1e0b1"])
        return json_schema
