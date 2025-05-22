from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters
from telegram import ChatPermissions
import datetime
from config import Config
from database import db
from utils.decorators import admin_only, group_only
from utils.helpers import mention_html, build_menu, extract_time
from utils.strings import Strings

@group_only
@admin_only
async def warn_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message and len(context.args) < 2:
        await update.message.reply_text("Usage: /warn <user> <reason> or reply to a message with /warn <reason>")
        return
    
    chat = update.effective_chat
    user = update.effective_user
    
    if update.message.reply_to_message:
        target_user = update.message.reply_to_message.from_user
        reason = " ".join(context.args) if context.args else "No reason given"
    else:
        try:
            target_user = await context.bot.get_chat(context.args[0])
            reason = " ".join(context.args[1:]) if len(context.args) > 1 else "No reason given"
        except:
            await update.message.reply_text("User not found.")
            return
    
    if target_user.id == context.bot.id:
        await update.message.reply_text("I can't warn myself!")
        return
    
    if target_user.id == user.id:
        await update.message.reply_text("You can't warn yourself!")
        return
    
    await db.add_warn(target_user.id, chat.id, reason, user.id)
    warns = await db.get_warns(target_user.id, chat.id)
    
    warn_limit = 3  # Default warn limit
    if len(warns) >= warn_limit:
        try:
            await chat.ban_member(target_user.id)
            await update.message.reply_text(
                f"🚫 {mention_html(target_user.id, target_user.first_name)} has been banned "
                f"for reaching {warn_limit} warnings."
            )
            await db.remove_warns(target_user.id, chat.id)
            return
        except Exception as e:
            await update.message.reply_text(f"Failed to ban user: {e}")
            return
    
    await update.message.reply_text(
        f"⚠️ {mention_html(target_user.id, target_user.first_name)} has been warned.\n"
        f"📝 Reason: {reason}\n"
        f"🔢 Warns: {len(warns)}/{warn_limit}",
        parse_mode="HTML"
    )

@group_only
@admin_only
async def unwarn_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message and len(context.args) < 1:
        await update.message.reply_text("Usage: /unwarn <user> or reply to a message with /unwarn")
        return
    
    chat = update.effective_chat
    
    if update.message.reply_to_message:
        target_user = update.message.reply_to_message.from_user
    else:
        try:
            target_user = await context.bot.get_chat(context.args[0])
        except:
            await update.message.reply_text("User not found.")
            return
    
    warns = await db.get_warns(target_user.id, chat.id)
    if not warns:
        await update.message.reply_text("This user has no warnings!")
        return
    
    await db.remove_warns(target_user.id, chat.id)
    await update.message.reply_text(
        f"✅ All warnings for {mention_html(target_user.id, target_user.first_name)} have been removed.",
        parse_mode="HTML"
    )

@group_only
@admin_only
async def ban_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message and len(context.args) < 1:
        await update.message.reply_text("Usage: /ban <user> <reason> or reply to a message with /ban <reason>")
        return
    
    chat = update.effective_chat
    user = update.effective_user
    
    if update.message.reply_to_message:
        target_user = update.message.reply_to_message.from_user
        reason = " ".join(context.args) if context.args else "No reason given"
    else:
        try:
            target_user = await context.bot.get_chat(context.args[0])
            reason = " ".join(context.args[1:]) if len(context.args) > 1 else "No reason given"
        except:
            await update.message.reply_text("User not found.")
            return
    
    if target_user.id == context.bot.id:
        await update.message.reply_text("I can't ban myself!")
        return
    
    if target_user.id == user.id:
        await update.message.reply_text("You can't ban yourself!")
        return
    
    try:
        await chat.ban_member(target_user.id)
        await update.message.reply_text(
            f"🚫 {mention_html(target_user.id, target_user.first_name)} has been banned.\n"
            f"📝 Reason: {reason}",
            parse_mode="HTML"
        )
    except Exception as e:
        await update.message.reply_text(f"Failed to ban user: {e}")

@group_only
@admin_only
async def unban_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message and len(context.args) < 1:
        await update.message.reply_text("Usage: /unban <user> or reply to a message with /unban")
        return
    
    chat = update.effective_chat
    
    if update.message.reply_to_message:
        target_user = update.message.reply_to_message.from_user
    else:
        try:
            target_user = await context.bot.get_chat(context.args[0])
        except:
            await update.message.reply_text("User not found.")
            return
    
    try:
        await chat.unban_member(target_user.id)
        await update.message.reply_text(
            f"✅ {mention_html(target_user.id, target_user.first_name)} has been unbanned.",
            parse_mode="HTML"
        )
    except Exception as e:
        await update.message.reply_text(f"Failed to unban user: {e}")

@group_only
@admin_only
async def mute_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message and len(context.args) < 1:
        await update.message.reply_text("Usage: /mute <user> <time> <reason> or reply to a message with /mute <time> <reason>")
        return
    
    chat = update.effective_chat
    user = update.effective_user
    
    if update.message.reply_to_message:
        target_user = update.message.reply_to_message.from_user
        time_val = context.args[0] if context.args else None
        reason = " ".join(context.args[1:]) if len(context.args) > 1 else "No reason given"
    else:
        try:
            target_user = await context.bot.get_chat(context.args[0])
            time_val = context.args[1] if len(context.args) > 1 else None
            reason = " ".join(context.args[2:]) if len(context.args) > 2 else "No reason given"
        except:
            await update.message.reply_text("User not found.")
            return
    
    if target_user.id == context.bot.id:
        await update.message.reply_text("I can't mute myself!")
        return
    
    if target_user.id == user.id:
        await update.message.reply_text("You can't mute yourself!")
        return
    
    try:
        if time_val:
            mute_time = extract_time(time_val)
            if not mute_time:
                await update.message.reply_text("Invalid time format. Use: 30m, 1h, 1d")
                return
            
            until_date = datetime.datetime.now() + datetime.timedelta(seconds=mute_time)
            await chat.restrict_member(
                target_user.id,
                until_date=until_date,
                permissions=ChatPermissions(
                    can_send_messages=False,
                    can_send_media_messages=False,
                    can_send_other_messages=False,
                    can_add_web_page_previews=False
                )
            )
            time_str = f"for {time_val}"
        else:
            await chat.restrict_member(
                target_user.id,
                permissions=ChatPermissions(
                    can_send_messages=False,
                    can_send_media_messages=False,
                    can_send_other_messages=False,
                    can_add_web_page_previews=False
                )
            )
            time_str = "indefinitely"
        
        await update.message.reply_text(
            f"🔇 {mention_html(target_user.id, target_user.first_name)} has been muted {time_str}.\n"
            f"📝 Reason: {reason}",
            parse_mode="HTML"
        )
    except Exception as e:
        await update.message.reply_text(f"Failed to mute user: {e}")

@group_only
@admin_only
async def unmute_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message and len(context.args) < 1:
        await update.message.reply_text("Usage: /unmute <user> or reply to a message with /unmute")
        return
    
    chat = update.effective_chat
    
    if update.message.reply_to_message:
        target_user = update.message.reply_to_message.from_user
    else:
        try:
            target_user = await context.bot.get_chat(context.args[0])
        except:
            await update.message.reply_text("User not found.")
            return
    
    try:
        await chat.restrict_member(
            target_user.id,
            permissions=ChatPermissions(
                can_send_messages=True,
                can_send_media_messages=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True
            )
        )
        await update.message.reply_text(
            f"🔊 {mention_html(target_user.id, target_user.first_name)} has been unmuted.",
            parse_mode="HTML"
        )
    except Exception as e:
        await update.message.reply_text(f"Failed to unmute user: {e}")

@group_only
@admin_only
async def kick_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message and len(context.args) < 1:
        await update.message.reply_text("Usage: /kick <user> <reason> or reply to a message with /kick <reason>")
        return
    
    chat = update.effective_chat
    user = update.effective_user
    
    if update.message.reply_to_message:
        target_user = update.message.reply_to_message.from_user
        reason = " ".join(context.args) if context.args else "No reason given"
    else:
        try:
            target_user = await context.bot.get_chat(context.args[0])
            reason = " ".join(context.args[1:]) if len(context.args) > 1 else "No reason given"
        except:
            await update.message.reply_text("User not found.")
            return
    
    if target_user.id == context.bot.id:
        await update.message.reply_text("I can't kick myself!")
        return
    
    if target_user.id == user.id:
        await update.message.reply_text("You can't kick yourself!")
        return
    
    try:
        await chat.ban_member(target_user.id)
        await chat.unban_member(target_user.id)
        await update.message.reply_text(
            f"👢 {mention_html(target_user.id, target_user.first_name)} has been kicked.\n"
            f"📝 Reason: {reason}",
            parse_mode="HTML"
        )
    except Exception as e:
        await update.message.reply_text(f"Failed to kick user: {e}")

@group_only
@admin_only
async def pin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        await update.message.reply_text("Please reply to a message to pin it.")
        return
    
    try:
        await update.message.reply_to_message.pin()
        await update.message.reply_text("📌 Message pinned!")
    except Exception as e:
        await update.message.reply_text(f"Failed to pin message: {e}")

@group_only
@admin_only
async def unpin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await context.bot.unpin_chat_message(update.effective_chat.id)
        await update.message.reply_text("📌 Message unpinned!")
    except Exception as e:
        await update.message.reply_text(f"Failed to unpin message: {e}")

@group_only
@admin_only
async def setwelcome_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 1:
        await update.message.reply_text("Usage: /setwelcome <message> or /setwelcome default to reset")
        return
    
    if context.args[0].lower() == "default":
        await db.set_welcome(update.effective_chat.id, Config.DEFAULT_WELCOME)
        await update.message.reply_text("Welcome message reset to default.")
        return
    
    welcome_message = " ".join(context.args)
    await db.set_welcome(update.effective_chat.id, welcome_message)
    await update.message.reply_text("Welcome message updated!")

@group_only
@admin_only
async def setgoodbye_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 1:
        await update.message.reply_text("Usage: /setgoodbye <message> or /setgoodbye default to reset")
        return
    
    if context.args[0].lower() == "default":
        await db.set_goodbye(update.effective_chat.id, Config.DEFAULT_GOODBYE)
        await update.message.reply_text("Goodbye message reset to default.")
        return
    
    goodbye_message = " ".join(context.args)
    await db.set_goodbye(update.effective_chat.id, goodbye_message)
    await update.message.reply_text("Goodbye message updated!")

@group_only
@admin_only
async def clean_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 1:
        await update.message.reply_text("Usage: /clean <amount>")
        return
    
    try:
        amount = int(context.args[0])
        if amount > 100:
            await update.message.reply_text("You can only clean up to 100 messages at a time.")
            return
        
        for msg_id in range(update.message.message_id - amount, update.message.message_id):
            try:
                await context.bot.delete_message(update.effective_chat.id, msg_id)
            except:
                continue
        await update.message.reply_text(f"🧹 Cleaned {amount} messages.")
    except ValueError:
        await update.message.reply_text("Please provide a valid number.")

@group_only
@admin_only
async def setrules_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 1:
        await update.message.reply_text("Usage: /setrules <rules text>")
        return
    
    rules_text = " ".join(context.args)
    await db.settings.update_one(
        {"chat_id": update.effective_chat.id},
        {"$set": {"rules": rules_text, "timestamp": datetime.datetime.now()}},
        upsert=True
    )
    await update.message.reply_text("Rules updated!")

@group_only
async def rules_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    settings = await db.settings.find_one({"chat_id": update.effective_chat.id})
    if not settings or "rules" not in settings:
        await update.message.reply_text("No rules set for this group.")
        return
    
    await update.message.reply_text(f"📜 <b>Group Rules:</b>\n\n{settings['rules']}", parse_mode="HTML")

@group_only
@admin_only
async def save_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 1 or not update.message.reply_to_message:
        await update.message.reply_text("Usage: Reply to a message with /save <name>")
        return
    
    note_name = context.args[0].lower()
    replied_msg = update.message.reply_to_message
    
    if replied_msg.text:
        content = replied_msg.text
        msgtype = "text"
    elif replied_msg.caption:
        content = replied_msg.caption
        msgtype = replied_msg.content_type
    else:
        content = ""
        msgtype = replied_msg.content_type
    
    await db.add_note(
        update.effective_chat.id,
        note_name,
        content,
        msgtype
    )
    
    if replied_msg.content_type != "text":
        await db.notes.update_one(
            {"chat_id": update.effective_chat.id, "name": note_name},
            {"$set": {"file_id": replied_msg[replied_msg.content_type].file_id, "timestamp": datetime.datetime.now()}},
            upsert=True
        )
    
    await update.message.reply_text(f"Note '{note_name}' saved!")

@group_only
async def get_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 1:
        await update.message.reply_text("Usage: /get <name>")
        return
    
    note_name = context.args[0].lower()
    note = await db.get_note(update.effective_chat.id, note_name)
    
    if not note:
        await update.message.reply_text("Note not found!")
        return
    
    if note["msgtype"] == "text":
        await update.message.reply_text(note["content"])
    else:
        await context.bot.send_document(
            chat_id=update.effective_chat.id,
            document=note["file_id"],
            caption=note.get("content", "")
        )

@group_only
@admin_only
async def clear_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 1:
        await update.message.reply_text("Usage: /clear <name>")
        return
    
    note_name = context.args[0].lower()
    await db.delete_note(update.effective_chat.id, note_name)
    await update.message.reply_text(f"Note '{note_name}' deleted!")

@group_only
async def notes_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    notes = await db.get_notes(update.effective_chat.id)
    if not notes:
        await update.message.reply_text("No notes in this chat!")
        return
    
    note_list = "\n".join([f"• {note['name']}" for note in notes])
    await update.message.reply_text(f"📝 <b>Notes in this chat:</b>\n\n{note_list}", parse_mode="HTML")

@group_only
@admin_only
async def filter_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2 or not update.message.reply_to_message:
        await update.message.reply_text("Usage: Reply to a message with /filter <keyword>")
        return
    
    keyword = context.args[0].lower()
    replied_msg = update.message.reply_to_message
    
    if replied_msg.text:
        content = replied_msg.text
        msgtype = "text"
    elif replied_msg.caption:
        content = replied_msg.caption
        msgtype = replied_msg.content_type
    else:
        content = ""
        msgtype = replied_msg.content_type
    
    await db.add_filter(
        update.effective_chat.id,
        keyword,
        content,
        msgtype
    )
    
    if replied_msg.content_type != "text":
        await db.filters.update_one(
            {"chat_id": update.effective_chat.id, "keyword": keyword},
            {"$set": {"file_id": replied_msg[replied_msg.content_type].file_id, "timestamp": datetime.datetime.now()}},
            upsert=True
        )
    
    await update.message.reply_text(f"Filter '{keyword}' added!")

@group_only
@admin_only
async def stop_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 1:
        await update.message.reply_text("Usage: /stop <keyword>")
        return
    
    keyword = context.args[0].lower()
    await db.delete_filter(update.effective_chat.id, keyword)
    await update.message.reply_text(f"Filter '{keyword}' removed!")

@group_only
async def filters_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    filters = await db.get_filters(update.effective_chat.id)
    if not filters:
        await update.message.reply_text("No filters in this chat!")
        return
    
    filter_list = "\n".join([f"• {filt['keyword']}" for filt in filters])
    await update.message.reply_text(f"🔍 <b>Filters in this chat:</b>\n\n{filter_list}", parse_mode="HTML")

async def group_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    if chat.type != "private":
        is_private = chat.type == "private" or not hasattr(chat, 'username') or not chat.username
        if not await db.is_chat_registered(chat.id):
            await db.add_chat(chat.id, chat.title, is_private)
        
        # Anti-spam check
        user_id = update.effective_user.id
        if context.user_data.get("last_message_time"):
            last_time = context.user_data["last_message_time"]
            if (datetime.datetime.now() - last_time).total_seconds() < 2:
                context.user_data["spam_count"] = context.user_data.get("spam_count", 0) + 1
                if context.user_data["spam_count"] >= 5:
                    await update.message.reply_text(
                        f"⚠️ {mention_html(user_id, update.effective_user.first_name)}, please slow down! You're sending messages too quickly."
                    )
                    return
            else:
                context.user_data["spam_count"] = 0
        context.user_data["last_message_time"] = datetime.datetime.now()
        
        # Check filters
        chat_filters = await db.get_filters(chat.id)
        if chat_filters and update.message.text:
            text = update.message.text.lower()
            for filt in chat_filters:
                if filt["keyword"] in text:
                    if filt["msgtype"] == "text":
                        await update.message.reply_text(filt["content"])
                    else:
                        await context.bot.send_document(
                            chat_id=chat.id,
                            document=filt["file_id"],
                            caption=filt.get("content", "")
                        )
                    break

group_handlers = [
    CommandHandler("warn", warn_command),
    CommandHandler("unwarn", unwarn_command),
    CommandHandler("ban", ban_command),
    CommandHandler("unban", unban_command),
    CommandHandler("mute", mute_command),
    CommandHandler("unmute", unmute_command),
    CommandHandler("kick", kick_command),
    CommandHandler("pin", pin_command),
    CommandHandler("unpin", unpin_command),
    CommandHandler("setwelcome", setwelcome_command),
    CommandHandler("setgoodbye", setgoodbye_command),
    CommandHandler("clean", clean_command),
    CommandHandler("setrules", setrules_command),
    CommandHandler("rules", rules_command),
    CommandHandler("save", save_command),
    CommandHandler("get", get_command),
    CommandHandler("clear", clear_command),
    CommandHandler("notes", notes_command),
    CommandHandler("filter", filter_command),
    CommandHandler("stop", stop_command),
    CommandHandler("filters", filters_command),
]