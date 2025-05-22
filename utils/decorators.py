from telegram import Update
from telegram.ext import ContextTypes
from functools import wraps
from config import Config

def group_only(func):
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        if update.effective_chat.type == "private":
            await update.message.reply_text("This command can only be used in groups!")
            return
        return await func(update, context, *args, **kwargs)
    return wrapper

def admin_only(func):
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user = update.effective_user
        chat = update.effective_chat
        
        if chat.type == "private":
            return await func(update, context, *args, **kwargs)
        
        admins = await chat.get_administrators()
        is_admin = any(admin.user.id == user.id for admin in admins)
        
        if not is_admin:
            await update.message.reply_text("You need to be an admin to use this command!")
            return
        
        return await func(update, context, *args, **kwargs)
    return wrapper

def owner_only(func):
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        if update.effective_user.id != Config.OWNER_ID:
            await update.message.reply_text("This command is only for the bot owner!")
            return
        return await func(update, context, *args, **kwargs)
    return wrapper