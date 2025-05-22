from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler
from config import Config
from database import db
from utils.decorators import owner_only
import uuid

@owner_only
async def post_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        await update.message.reply_text("Please reply to a message to post it to all groups.")
        return
    
    buttons = [
        InlineKeyboardButton("✅ Confirm Post", callback_data=f"confirm_post_{uuid.uuid4()}"),
        InlineKeyboardButton("❌ Cancel", callback_data="cancel_post"),
    ]
    
    try:
        await update.message.reply_text(
            f"📢 <b>Post Preview</b>\n\n"
            f"Are you sure you want to post this message to all groups?",
            reply_markup=InlineKeyboardMarkup([buttons]),
            parse_mode="HTML"
        )
    except Exception as e:
        await update.message.reply_text(f"Error initiating post: {e}")
        await send_error_log(context, update.effective_user.id, f"Post command error: {e}")

async def confirm_post_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    original_message = query.message.reply_to_message
    if not original_message:
        await query.edit_message_text("Error: Original message not found.")
        return
    
    chats = await db.get_all_chats()
    success = 0
    failed = 0
    
    await query.edit_message_text("📤 Starting to post to all groups...")
    
    try:
        for chat in chats:
            try:
                if original_message.text or original_message.caption:
                    if original_message.photo:
                        await context.bot.send_photo(
                            chat_id=chat["chat_id"],
                            photo=original_message.photo[-1].file_id,
                            caption=original_message.caption or original_message.text or "",
                            parse_mode="HTML"
                        )
                    elif original_message.video:
                        await context.bot.send_video(
                            chat_id=chat["chat_id"],
                            video=original_message.video.file_id,
                            caption=original_message.caption or original_message.text or "",
                            parse_mode="HTML"
                        )
                    elif original_message.sticker:
                        await context.bot.send_sticker(
                            chat_id=chat["chat_id"],
                            sticker=original_message.sticker.file_id
                        )
                    elif original_message.animation:
                        await context.bot.send_animation(
                            chat_id=chat["chat_id"],
                            animation=original_message.animation.file_id,
                            caption=original_message.caption or original_message.text or "",
                            parse_mode="HTML"
                        )
                    else:
                        await context.bot.send_message(
                            chat_id=chat["chat_id"],
                            text=original_message.text or original_message.caption or "",
                            parse_mode="HTML"
                        )
                else:
                    await context.bot.copy_message(
                        chat_id=chat["chat_id"],
                        from_chat_id=original_message.chat_id,
                        message_id=original_message.message_id
                    )
                success += 1
            except Exception as e:
                failed += 1
                await send_error_log(context, update.effective_user.id, f"Post to chat {chat['chat_id']} failed: {e}")
                continue
        
        await query.edit_message_text(
            f"✅ <b>Posting Complete</b>\n\n"
            f"• Success: {success}\n"
            f"• Failed: {failed}",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back", callback_data="owner_back")]
            ])
        )
    except Exception as e:
        await query.edit_message_text(f"Error completing post: {e}")
        await send_error_log(context, update.effective_user.id, f"Post callback error: {e}")

async def cancel_post_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "❌ Posting cancelled.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back", callback_data="owner_back")]
        ])
    )

async def send_error_log(context: ContextTypes.DEFAULT_TYPE, user_id: int, error: str):
    if user_id == Config.OWNER_ID:
        try:
            await context.bot.send_message(
                chat_id=Config.OWNER_ID,
                text=f"⚠️ Error Log:\n\n{error}",
                parse_mode="HTML"
            )
        except:
            pass

post_handlers = [
    CommandHandler("post", post_command),
    CallbackQueryHandler(confirm_post_callback, pattern="^confirm_post_.*$"),
    CallbackQueryHandler(cancel_post_callback, pattern="^cancel_post$"),
]