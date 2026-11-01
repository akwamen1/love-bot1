import asyncio
import os
from aiohttp import web
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import LabeledPrice, PreCheckoutQuery, Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from dotenv import load_dotenv

load_dotenv()

# --- НАСТРОЙКИ ---
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL") # Например: https://love-bot-sdya.onrender.com
STARS_PRICE = 20
# -----------------

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

def get_main_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="💘 Узнать совместимость", callback_data="ask_names")
    builder.adjust(1)
    return builder.as_markup()

def calculate_compatibility(name1: str, name2: str) -> int:
    total = sum(ord(c) for c in name1.lower()) + sum(ord(c) for c in name2.lower())
    return total % 101

@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        f"Привет, {message.from_user.first_name}! 👋\n\n"
        "Нажми на кнопку ниже, чтобы узнать совместимость имен! 💘\n\n"
        f"Стоимость — {STARS_PRICE} ⭐ (Telegram Stars).\n"
        "⚠️ *Внимание:* это игра и развлечение.",
        parse_mode="Markdown",
        reply_markup=get_main_keyboard()
    )

@dp.callback_query(F.data == "ask_names")
async def ask_for_names(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer("Напиши два имени через запятую (например: *Аня, Ваня*):", parse_mode="Markdown")

@dp.message(F.text.contains(","))
async def send_stars_invoice(message: Message):
    parts = [p.strip() for p in message.text.split(",")]
    if len(parts) != 2 or not parts[0] or not parts[1]:
        await message.answer("Нужно ровно два имени. Попробуй ещё раз: `Имя1, Имя2`", parse_mode="Markdown")
        return

    name1, name2 = parts[0], parts[1]
    
    await bot.send_invoice(
        chat_id=message.chat.id,
        title="Совместимость имён",
        description=f"Расчёт для пары: {name1} и {name2}",
        payload=f"{name1}|{name2}",
        provider_token="",
        currency="XTR",
        prices=[LabeledPrice(label="Совместимость", amount=STARS_PRICE)]
    )

@dp.pre_checkout_query()
async def process_pre_checkout_query(pre_checkout_query: PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

@dp.message(F.successful_payment)
async def process_successful_payment(message: Message):
    payload = message.successful_payment.invoice_payload
    name1, name2 = payload.split("|")
    
    percent = calculate_compatibility(name1, name2)
    
    if percent > 80:
        verdict = "🔥 Это судьба! Вам точно нужно быть вместе."
    elif percent > 50:
        verdict = "😊 Хорошая пара, есть все шансы."
    elif percent > 20:
        verdict = "🤔 Так себе... Но попробовать можно."
    else:
        verdict = "💔 Лучше остаться друзьями."

    await message.answer(
        f"✅ Оплата прошла! Спасибо! ⭐\n\n"
        f"💞 *{name1}* и *{name2}*\n\n"
        f"Совместимость: *{percent}%*\n"
        f"{verdict}",
        parse_mode="Markdown",
        reply_markup=get_main_keyboard()
    )

async def on_startup(bot: Bot):
    await bot.set_webhook(f"{WEBHOOK_URL}/{BOT_TOKEN}")
    print(f"Вебхук установлен на {WEBHOOK_URL}/{BOT_TOKEN}")

def main():
    app = web.Application()
    
    # Обработчик вебхуков от Telegram
    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
    )
    webhook_requests_handler.register(app, path=f"/{BOT_TOKEN}")
    
    # Проверка для UptimeRobot
    async def health(request):
        return web.Response(text="OK")
    app.router.add_get('/health', health)
    
    # Привязка старта
    dp.startup.register(on_startup)
    setup_application(app, dp, bot=bot)
    
    port = int(os.environ.get("PORT", 8080))
    web.run_app(app, host="0.0.0.0", port=port)

if __name__ == '__main__':
    main()