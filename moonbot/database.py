from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

class Database:
    def __init__(self):
        mongo_uri = os.getenv("MONGO_URI")
        self.client = MongoClient(mongo_uri)
        self.db = self.client["MoonBot"]
        self.groups = self.db["groups"]
        self.users = self.db["users"]

    def add_group(self, group_id, settings=None):
        """Add or update group settings."""
        if not settings:
            settings = {"welcome_enabled": True, "filters": [], "warnings": {}}
        self.groups.update_one({"group_id": group_id}, {"$set": settings}, upsert=True)

    def get_group(self, group_id):
        """Retrieve group settings."""
        return self.groups.find_one({"group_id": group_id})

    def add_warning(self, group_id, user_id, reason):
        """Add a warning for a user in a group."""
        group = self.get_group(group_id)
        warnings = group.get("warnings", {})
        user_warnings = warnings.get(str(user_id), [])
        user_warnings.append(reason)
        warnings[str(user_id)] = user_warnings
        self.groups.update_one({"group_id": group_id}, {"$set": {"warnings": warnings}})

    def get_warnings(self, group_id, user_id):
        """Get warnings for a user in a group."""
        group = self.get_group(group_id)
        return group.get("warnings", {}).get(str(user_id), [])

db = Database()