import asyncio
import os
from datetime import datetime, timedelta

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message
from aiohttp import web

from config import BOT_TOKEN
from database import init_db, add_task, get_tasks, add_reminder
from file_handler import summarize_text, extract_tasks
from voice_handler import transcribe_voice
from reminders import start_scheduler

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ===== КОМАНДЫ =====

@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "👋 Привет! Я твой личный ассистент.\n\n"
        "📋 Команды:\n"
        "/task <текст> — добавить задачу\n"
        "/tasks — список задач\n"
        "/remind <минуты> <текст> — напоминание\n"
        "📎 Пришли файл .txt — сделаю выжимку и задачи\n"
        "🎙 Пришли голосовое — распознаю текст"
    )

@dp.message(Command("task"))
async def cmd_task(message: Message):
    text = message.text.replace("/task", "").strip()
    if not text:
        await message.answer("❌ Напиши задачу после команды: /task Купить молоко")
        return
    add_task(message.from_user.id, text)
    await message.answer(f"✅ Задача добавлена: {text}")

@dp.message(Command("tasks"))
async def cmd_tasks(message: Message):
    tasks = get_tasks(message.from_user.id)
    if not tasks:
        await message.answer("📭 Задач пока нет")
        return
    text = "📋 Твои задачи:\n\n"
    for t_id, title, deadline, status in tasks:
        status_icon = "✅" if status == "done" else "⏳"
        dl = f" (до {deadline})" if deadline else ""
        text += f"{status_icon} {title}{dl}\n"
    await message.answer(text)

@dp.message(Command("remind"))
async def cmd_remind(message: Message):
    parts = message.text.replace("/remind", "").strip().split(" ", 1)
    if len(parts) < 2:
        await message.answer("❌ Формат: /remind 30 Купить молоко (через N минут)")
        return
    try:
        minutes = int(parts[0])
    except ValueError:
        await message.answer("❌ Первым словом должно быть число минут")
        return
    
    remind_text = parts[1]
    remind_at = (datetime.now() + timedelta(minutes=minutes)).isoformat()
    add_reminder(message.from_user.id, remind_text, remind_at)
    await message.answer(f"⏰ Напомню через {minutes} мин: {remind_text}")

# ===== ФАЙЛЫ =====

@dp.message(F.document)
async def handle_document(message: Message):
    doc = message.document
    if doc.file_size > 5 * 1024 * 1024:
        await message.answer("❌ Файл слишком большой (макс. 5 МБ)")
        return
    
    await message.answer("📄 Скачиваю файл...")
    file = await bot.get_file(doc.file_id)
    file_path = f"temp_{doc.file_name}"
    await bot.download_file(file.file_path, file_path)
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except Exception as e:
        await message.answer(f"❌ Не удалось прочитать файл: {e}")
        if os.path.exists(file_path):
            os.remove(file_path)
        return
    
    await message.answer("🧠 Делаю выжимку...")
    summary = await summarize_text(content)
    await message.answer(f"📝 Краткая выжимка:\n\n{summary}")
    
    await message.answer("📋 Извлекаю задачи...")
    tasks = await extract_tasks(content)
    if tasks:
        for task in tasks:
            add_task(message.from_user.id, task)
        tasks_text = "\n".join([f"• {t}" for t in tasks])
        await message.answer(f"✅ Добавлены задачи:\n\n{tasks_text}")
    else:
        await message.answer("Задач в файле не найдено")
    
    os.remove(file_path)

# ===== ГОЛОСОВЫЕ =====

@dp.message(F.voice)
async def handle_voice(message: Message):
    await message.answer("🎙 Распознаю голосовое...")
    file = await bot.get_file(message.voice.file_id)
    ogg_path = f"voice_{message.message_id}.ogg"
    await bot.download_file(file.file_path, ogg_path)
    
    text = await transcribe_voice(ogg_path)
    await message.answer(f"📝 Распознанный текст:\n\n{text}")
    
    add_task(message.from_user.id, text, description="Из голосового сообщения")
    await message.answer("✅ Добавлено в задачи")

# ===== ВЕБ-СЕРВЕР (для Render.com) =====

async def health(request):
    return web.Response(text="Bot is running!")

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', health)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    print(f"🌐 Web server started on port {port}")

# ===== ЗАПУСК =====

async def main():
    init_db()
    start_scheduler(bot)
    
    # Запускаем веб-сервер и бота параллельно
    await asyncio.gather(
        start_web_server(),
        dp.start_polling(bot)
    )

if __name__ == "__main__":
    asyncio.run(main())