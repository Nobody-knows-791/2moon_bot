from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def is_admin(update, context, user_id):
    """Check if a user is an admin in the chat."""
    chat = update.effective_chat
    admins = context.bot.get_chat_administrators(chat.id)
    return any(admin.user.id == user_id for admin in admins)

def format_welcome_message(user):
    """Format a welcome message with emojis."""
    return f"🌙 *Welcome, {user.first_name}!* 🌙\n" \
           f"Enjoy your stay in our group! Follow the rules to keep the vibe awesome! 😎"

def owner_keyboard():
    """Create an inline keyboard for owner commands."""
    keyboard = [
        [InlineKeyboardButton("📢 Post to Groups", callback_data="post")],
        [InlineKeyboardButton("⚙️ Bot Settings", callback_data="settings")]
    ]
    return InlineKeyboardMarkup(keyboard)