from motor.motor_asyncio import AsyncIOMotorClient
from config import Config
import datetime

class Database:
    def __init__(self):
        self._client = AsyncIOMotorClient(Config.MONGO_URI)
        self.db = self._client["MoonBot"]
        self.col = self.db["groups"]
        self.users = self.db["users"]
        self.settings = self.db["settings"]
        self.warns = self.db["warns"]
        self.notes = self.db["notes"]
        self.filters = self.db["filters"]
        self.chats = self.db["chats"]
        self.gbans = self.db["gbans"]
        self.afk = self.db["afk"]

    async def cleanup_old_data(self):
        """Cleanup old data (warns, notes, filters older than 30 days)"""
        thirty_days_ago = datetime.datetime.now() - datetime.timedelta(days=30)
        await self.warns.delete_many({"timestamp": {"$lt": thirty_days_ago}})
        await self.notes.delete_many({"timestamp": {"$lt": thirty_days_ago}})
        await self.filters.delete_many({"timestamp": {"$lt": thirty_days_ago}})

    async def add_chat(self, chat_id, chat_title, is_private=False):
        await self.chats.update_one(
            {"chat_id": chat_id},
            {"$set": {"chat_title": chat_title, "is_private": is_private, "timestamp": datetime.datetime.now()}},
            upsert=True
        )
    
    async def get_chat(self, chat_id):
        return await self.chats.find_one({"chat_id": chat_id})
    
    async def is_chat_registered(self, chat_id):
        chat = await self.get_chat(chat_id)
        return bool(chat)
    
    async def add_user(self, user_id, username, first_name):
        await self.users.update_one(
            {"user_id": user_id},
            {"$set": {"username": username, "first_name": first_name, "timestamp": datetime.datetime.now()}},
            upsert=True
        )
    
    async def get_user(self, user_id):
        return await self.users.find_one({"user_id": user_id})
    
    async def get_all_chats(self):
        return await self.chats.find({}).to_list(None)
    
    async def get_all_users(self):
        return await self.users.find({}).to_list(None)
    
    async def get_chat_count(self):
        return await self.chats.count_documents({})
    
    async def get_user_count(self):
        return await self.users.count_documents({})
    
    async def set_welcome(self, chat_id, welcome_message):
        await self.settings.update_one(
            {"chat_id": chat_id},
            {"$set": {"welcome": welcome_message, "timestamp": datetime.datetime.now()}},
            upsert=True
        )
    
    async def get_welcome(self, chat_id):
        setting = await self.settings.find_one({"chat_id": chat_id})
        return setting.get("welcome", Config.DEFAULT_WELCOME) if setting else Config.DEFAULT_WELCOME
    
    async def set_goodbye(self, chat_id, goodbye_message):
        await self.settings.update_one(
            {"chat_id": chat_id},
            {"$set": {"goodbye": goodbye_message, "timestamp": datetime.datetime.now()}},
            upsert=True
        )
    
    async def get_goodbye(self, chat_id):
        setting = await self.settings.find_one({"chat_id": chat_id})
        return setting.get("goodbye", Config.DEFAULT_GOODBYE) if setting else Config.DEFAULT_GOODBYE
    
    async def add_warn(self, user_id, chat_id, reason, warned_by):
        await self.warns.insert_one({
            "user_id": user_id,
            "chat_id": chat_id,
            "reason": reason,
            "warned_by": warned_by,
            "timestamp": datetime.datetime.now()
        })
    
    async def get_warns(self, user_id, chat_id):
        return await self.warns.find({"user_id": user_id, "chat_id": chat_id}).to_list(None)
    
    async def remove_warns(self, user_id, chat_id):
        await self.warns.delete_many({"user_id": user_id, "chat_id": chat_id})
    
    async def add_gban(self, user_id, reason, banned_by):
        await self.gbans.update_one(
            {"user_id": user_id},
            {"$set": {"reason": reason, "banned_by": banned_by, "timestamp": datetime.datetime.now()}},
            upsert=True
        )
    
    async def remove_gban(self, user_id):
        await self.gbans.delete_one({"user_id": user_id})
    
    async def is_gbanned(self, user_id):
        return await self.gbans.find_one({"user_id": user_id})
    
    async def add_note(self, chat_id, name, content, msgtype):
        await self.notes.update_one(
            {"chat_id": chat_id, "name": name},
            {"$set": {"content": content, "msgtype": msgtype, "timestamp": datetime.datetime.now()}},
            upsert=True
        )
    
    async def get_note(self, chat_id, name):
        return await self.notes.find_one({"chat_id": chat_id, "name": name})
    
    async def delete_note(self, chat_id, name):
        await self.notes.delete_one({"chat_id": chat_id, "name": name})
    
    async def get_notes(self, chat_id):
        return await self.notes.find({"chat_id": chat_id}).to_list(None)
    
    async def add_filter(self, chat_id, keyword, content, msgtype):
        await self.filters.update_one(
            {"chat_id": chat_id, "keyword": keyword},
            {"$set": {"content": content, "msgtype": msgtype, "timestamp": datetime.datetime.now()}},
            upsert=True
        )
    
    async def get_filter(self, chat_id, keyword):
        return await self.filters.find_one({"chat_id": chat_id, "keyword": keyword})
    
    async def delete_filter(self, chat_id, keyword):
        await self.filters.delete_one({"chat_id": chat_id, "keyword": keyword})
    
    async def get_filters(self, chat_id):
        return await self.filters.find({"chat_id": chat_id}).to_list(None)
    
    async def set_afk(self, user_id, reason):
        await self.afk.update_one(
            {"user_id": user_id},
            {"$set": {"reason": reason, "time": datetime.datetime.now()}},
            upsert=True
        )
    
    async def get_afk(self, user_id):
        return await self.afk.find_one({"user_id": user_id})
    
    async def del_afk(self, user_id):
        await self.afk.delete_one({"user_id": user_id})

db = Database()