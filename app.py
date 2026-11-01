import os
import asyncio
from flask import Flask, request
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import LabeledPrice, PreCheckoutQuery, Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.client.session.aiohttp import AiohttpSession

# --- НАСТРОЙКИ ---
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # Например: https://love-bot-sdya.onrender.com
STARS_PRICE = 20
# -----------------

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ... (здесь весь твой код с хэндлерами: /start, ask_names, send_stars_invoice и т.д.)
# Вставь сюда все функции-хэндлеры из твоего тгбот.py (cmd_start, ask_for_names, send_stars_invoice, process_pre_checkout_query, process_successful_payment)

app = Flask(__name__)

@app.route('/health')
def health():
    return "OK", 200

@app.route(f'/{BOT_TOKEN}', methods=['POST'])
async def webhook():
    # Этот эндпоинт принимает обновления от Telegram
    update = types.Update.model_validate(await request.get_json(), context={"bot": bot})
    await dp.feed_update(bot, update)
    return "OK", 200

async def main():
    # Устанавливаем вебхук
    await bot.set_webhook(url=f"{WEBHOOK_URL}/{BOT_TOKEN}")
    print(f"Webhook set to {WEBHOOK_URL}/{BOT_TOKEN}")
    # Flask будет запущен отдельно (см. ниже)

if __name__ == '__main__':
    # Запускаем установку вебхука в фоне
    asyncio.run(main())
    # Запускаем Flask (он будет обрабатывать входящие вебхуки)
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)