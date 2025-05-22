from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters
from config import Config
from database import db
from utils.decorators import group_only
from utils.helpers import mention_html
import datetime

@group_only
async def afk_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    reason = " ".join(context.args) if context.args else "No reason provided"
    
    await db.set_afk(user.id, reason)
    await update.message.reply_text(
        f"🌙 {mention_html(user.id, user.first_name)} is now AFK.\n"
        f"📝 Reason: {reason}",
        parse_mode="HTML"
    )

@group_only
async def afk_check_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat = update.effective_chat
    message = update.message
    
    # Check if user is returning from AFK
    afk_data = await db.get_afk(user.id)
    if afk_data:
        time_diff = (datetime.datetime.now() - afk_data["time"]).total_seconds()
        await db.del_afk(user.id)
        await message.reply_text(
            f"🌙 {mention_html(user.id, user.first_name)} is back!\n"
            f"⏰ Was AFK for {int(time_diff // 60)} minute(s).",
            parse_mode="HTML"
        )
    
    # Check for mentions of AFK users
    if message.entities:
        for entity in message.entities:
            if entity.type == "mention" or entity.type == "text_mention":
                mentioned_user = entity.user if entity.type == "text_mention" else None
                if not mentioned_user and entity.type == "mention":
                    try:
                        username = message.text[entity.offset:entity.offset + entity.length]
                        mentioned_user = await context.bot.get_chat(username)
                    except:
                        continue
                
                if mentioned_user:
                    afk_data = await db.get_afk(mentioned_user.id)
                    if afk_data:
                        time_diff = (datetime.datetime.now() - afk_data["time"]).total_seconds()
                        if time_diff < Config.AFK_TIMEOUT:
                            await message.reply_text(
                                f"🌙 {mention_html(mentioned_user.id, mentioned_user.first_name)} is AFK.\n"
                                f"📝 Reason: {afk_data['reason']}\n"
                                f"⏰ AFK for {int(time_diff // 60)} minute(s).",
                                parse_mode="HTML"
                            )

@group_only
async def end_afk_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    afk_data = await db.get_afk(user.id)
    if not afk_data:
        await update.message.reply_text("You are not AFK!")
        return
    
    time_diff = (datetime.datetime.now() - afk_data["time"]).total_seconds()
    await db.del_afk(user.id)
    await update.message.reply_text(
        f"🌙 {mention_html(user.id, user.first_name)} is no longer AFK.\n"
        f"⏰ Was AFK for {int(time_diff // 60)} minute(s).",
        parse_mode="HTML"
    )

async def afk_timeout_job(context: ContextTypes.DEFAULT_TYPE):
    afk_users = await db.afk.find({}).to_list(None)
    for afk_user in afk_users:
        time_diff = (datetime.datetime.now() - afk_user["time"]).total_seconds()
        if time_diff >= Config.AFK_TIMEOUT:
            await db.del_afk(afk_user["user_id"])

afk_handlers = [
    CommandHandler("afk", afk_command),
    CommandHandler("endafk", end_afk_command),
    MessageHandler(filters.TEXT & ~filters.COMMAND & filters.ChatType.GROUPS, afk_check_handler),
]