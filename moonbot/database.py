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
            settings = {
                "welcome_enabled": True,
                "welcome_message": None,  # Custom welcome message
                "filters": {},  # Keyword: response
                "warnings": {},  # user_id: [reasons]
                "locks": {},  # type: bool (e.g., {"media": False})
                "notes": {},  # hashtag: message
                "admins": [],  # List of admin user IDs
            }
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

    def set_welcome_message(self, group_id, message):
        """Set custom welcome message."""
        self.groups.update_one({"group_id": group_id}, {"$set": {"welcome_message": message}})

    def add_filter(self, group_id, keyword, response):
        """Add a filter."""
        group = self.get_group(group_id)
        filters = group.get("filters", {})
        filters[keyword] = response
        self.groups.update_one({"group_id": group_id}, {"$set": {"filters": filters}})

    def get_filters(self, group_id):
        """Get all filters."""
        group = self.get_group(group_id)
        return group.get("filters", {})

    def add_note(self, group_id, hashtag, message):
        """Add a note."""
        group = self.get_group(group_id)
        notes = group.get("notes", {})
        notes[hashtag] = message
        self.groups.update_one({"group_id": group_id}, {"$set": {"notes": notes}})

    def get_note(self, group_id, hashtag):
        """Get a note."""
        group = self.get_group(group_id)
        return group.get("notes", {}).get(hashtag)

    def set_lock(self, group_id, lock_type, value):
        """Set a lock (e.g., media, links)."""
        group = self.get_group(group_id)
        locks = group.get("locks", {})
        locks[lock_type] = value
        self.groups.update_one({"group_id": group_id}, {"$set": {"locks": locks}})

    def get_locks(self, group_id):
        """Get all locks."""
        group = self.get_group(group_id)
        return group.get("locks", {})

    def add_admin(self, group_id, user_id):
        """Add an admin."""
        group = self.get_group(group_id)
        admins = group.get("admins", [])
        if user_id not in admins:
            admins.append(user_id)
            self.groups.update_one({"group_id": group_id}, {"$set": {"admins": admins}})

    def remove_admin(self, group_id, user_id):
        """Remove an admin."""
        group = self.get_group(group_id)
        admins = group.get("admins", [])
        if user_id in admins:
            admins.remove(user_id)
            self.groups.update_one({"group_id": group_id}, {"$set": {"admins": admins}})

db = Database()