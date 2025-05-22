from config import Config

class Strings:
    HELP_MESSAGE = """
🌙 <b>{} - Help Menu</b> 🌙

✨ <b>User Commands</b>
/start - Start the bot and get the welcome menu
/help - Show this help menu
/info - Get info about yourself or another user
/id - Get chat and user IDs
/afk <reason> - Set your AFK status
/endafk - Remove your AFK status
/report - Report a message to admins
/rules - View group rules
/notes - List saved notes
/filters - List active filters
/get <name> - Retrieve a saved note
/admins - List group administrators
/ping - Check if the bot is online

👮‍♂️ <b>Admin Commands</b>
/warn <user> <reason> - Warn a user
/unwarn <user> - Remove warnings
/ban <user> <reason> - Ban a user
/unban <user> - Unban a user
/mute <user> <time> <reason> - Mute a user
/unmute <user> - Unmute a user
/kick <user> <reason> - Kick a user
/pin - Pin a replied message
/unpin - Unpin the pinned message
/setwelcome <message> - Set custom welcome message
/setgoodbye <message> - Set custom goodbye message
/clean <amount> - Delete recent messages
/setrules <text> - Set group rules
/save <name> - Save a note
/clear <name> - Delete a note
/filter <keyword> - Add a filter
/stop <keyword> - Remove a filter
/lock <type> - Lock chat features (messages, media, stickers, polls, links, bots)
/unlock <type> - Unlock chat features
/promote <user> - Promote a user to admin
/demote <user> - Demote a user from admin
/purge - Delete messages from replied message

👑 <b>Owner Commands (DM only)</b>
/stats - View bot statistics
/broadcast - Broadcast a message to all users and groups
/gban <user_id> <reason> - Globally ban a user
/ungban <user_id> - Remove global ban
/post - Post a message to all groups
/update - Update bot data
/logs - View error logs

📢 Join our support group: {}
📢 Follow our channel: https://t.me/chilling_friends_support
""".format(Config.BOT_NAME, Config.SUPPORT_CHAT_LINK)