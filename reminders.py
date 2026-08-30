from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from aiogram import Bot
from database import get_pending_reminders, mark_reminder_sent

scheduler = AsyncIOScheduler()

def start_scheduler(bot: Bot):
    scheduler.add_job(
        check_reminders,
        IntervalTrigger(minutes=1),
        args=[bot],
        id="reminder_job",
        replace_existing=True
    )
    scheduler.start()

async def check_reminders(bot: Bot):
    reminders = get_pending_reminders()
    for rem_id, user_id, text in reminders:
        try:
            await bot.send_message(user_id, f"⏰ Напоминание:\n{text}")
            mark_reminder_sent(rem_id)
        except Exception as e:
            print(f"Ошибка отправки напоминания: {e}")