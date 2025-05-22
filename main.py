from telegram.ext import Application, Defaults, PicklePersistence
from config import Config
from database import db
from handlers import all_handlers
from handlers.afk import afk_timeout_job
import asyncio
import logging

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

async def periodic_cleanup():
    while True:
        await db.cleanup_old_data()
        await asyncio.sleep(24 * 60 * 60)  # Run every 24 hours

async def main():
    defaults = Defaults(parse_mode="HTML")
    persistence = PicklePersistence(filepath="bot_persistence")
    
    app = (
        Application.builder()
        .token(Config.TOKEN)
        .defaults(defaults)
        .persistence(persistence)
        .build()
    )
    
    for handler in all_handlers:
        app.add_handler(handler)
    
    # Schedule periodic cleanup
    app.job_queue.run_repeating(afk_timeout_job, interval=60, first=10)
    asyncio.create_task(periodic_cleanup())
    
    await app.initialize()
    await app.start()
    await app.updater.start_polling(allowed_updates=["message", "chat_member", "callback_query"])
    
    # Keep the bot running
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    asyncio.run(main())