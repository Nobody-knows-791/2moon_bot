from telegram.ext import MessageHandler, filters
from .admin import admin_handlers
from .group import group_message_handler, group_handlers
from .users import user_handlers
from .welcome import welcome_handlers
from .post import post_handlers
from .moderation import moderation_handlers
from .afk import afk_handlers
from .report import report_handlers

all_handlers = (
    admin_handlers +
    group_handlers +
    user_handlers +
    welcome_handlers +
    post_handlers +
    moderation_handlers +
    afk_handlers +
    report_handlers +
    [MessageHandler(filters.ALL & ~filters.COMMAND, group_message_handler)]
)