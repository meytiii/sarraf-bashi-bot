import asyncio
import asyncio
import os
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, BufferedInputFile
from dotenv import load_dotenv

from api_fetcher import get_market_data
from image_generator import generate_price_banner

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

def get_main_keyboard():
    buttons = [
        [InlineKeyboardButton(text="🔄 دریافت قیمت‌های لحظه‌ای", callback_data="fetch_prices")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

@dp.message(CommandStart())
async def command_start_handler(message: types.Message) -> None:
    welcome_text = (
        "سلام! من «صراف‌باشی» هستم؛ دستیار سریع و رایگان شما برای چک کردن بازار. 💸\n\n"
        "اینجا می‌تونی در کسری از ثانیه قیمت لحظه‌ای ارزها و سکه‌های طلا رو ببینی.\n\n"
        "برای دریافت آخرین قیمت‌ها، روی دکمه زیر کلیک کنید 👇"
    )
    await message.answer(welcome_text, reply_markup=get_main_keyboard())

@dp.callback_query(F.data == "fetch_prices")
async def handle_fetch_prices(callback: CallbackQuery):
    await callback.message.edit_text("⏳ در حال دریافت اطلاعات از بازار... لطفا کمی صبر کنید.")
    
    data = await get_market_data()
    
    if data:
        result_text = (
            "📊 قیمت‌های لحظه‌ای بازار:\n\n"
            f"🇺🇸 دلار آمریکا: {data['usd']}\n"
            f"🇪🇺 یورو: {data['eur']}\n"
            f"🇬🇧 پوند انگلیس: {data['gbp']}\n"
            f"🇹🇷 لیر ترکیه: {data['try']}\n"
            f"🇮🇶 دینار عراق: {data['iqd']}\n\n"
            f"🥇 طلای 18 عیار: {data['gold_18k']}\n"
            f"🪙 سکه امامی: {data['coin_emami']}\n"
            f"🪙 نیم سکه: {data['coin_half']}\n"
            f"🪙 ربع سکه: {data['coin_quarter']}\n"
            f"🪙 سکه بهار آزادی: {data['coin_bahar']}\n"
            f"🥈 انس نقره: {data['silver_ounce']}\n\n"
            "⏱ به‌روزرسانی شده از سرور صراف‌باشی"
        )
    else:
        result_text = "❌ متاسفانه در ارتباط با سرور قیمت‌ها مشکلی پیش آمد. لطفا دقایقی دیگر دوباره تلاش کنید."
        
    await callback.message.edit_text(result_text, reply_markup=get_main_keyboard())

@dp.message(Command("price", "gheymat"))
async def command_price_handler(message: types.Message) -> None:
    status_msg = await message.answer("در حال دریافت اطلاعات از بازار... لطفا کمی صبر کنید.")
    
    data = await get_market_data()
    
    if data:
        result_text = (
            "📊 قیمت‌های لحظه‌ای بازار:\n\n"
            f"🇺🇸 دلار آمریکا: {data['usd']}\n"
            f"🇪🇺 یورو: {data['eur']}\n"
            f"🇬🇧 پوند انگلیس: {data['gbp']}\n"
            f"🇹🇷 لیر ترکیه: {data['try']}\n"
            f"🇮🇶 دینار عراق: {data['iqd']}\n\n"
            f"🥇 طلای 18 عیار: {data['gold_18k']}\n"
            f"🪙 سکه امامی: {data['coin_emami']}\n"
            f"🪙 نیم سکه: {data['coin_half']}\n"
            f"🪙 ربع سکه: {data['coin_quarter']}\n"
            f"🪙 سکه بهار آزادی: {data['coin_bahar']}\n"
            f"🥈 انس نقره: {data['silver_ounce']}\n\n"
            "⏱ به‌روزرسانی شده از سرور صراف‌باشی"
        )
    else:
        result_text = "متاسفانه در ارتباط با سرور قیمت‌ها مشکلی پیش آمد. لطفا دقایقی دیگر دوباره تلاش کنید."
        
    await status_msg.edit_text(result_text, reply_markup=get_main_keyboard())

# --- Natural Text Word Listeners ---

@dp.message(F.text.contains("دلار"))
async def group_usd_listener(message: types.Message):
    data = await get_market_data()
    if data and data['usd'] != "نامشخص":
        photo_bytes = generate_price_banner("usd", "قیمت دلار آمریکا", data['usd'])
        input_file = BufferedInputFile(photo_bytes.read(), filename="usd.png")
        await message.reply_photo(photo=input_file, caption="🇺🇸 قیمت لحظه‌ای دلار آمریکا (ریال)")

@dp.message(F.text.contains("سکه"))
async def group_coin_listener(message: types.Message):
    data = await get_market_data()
    if data and data['coin_emami'] != "نامشخص":
        photo_bytes = generate_price_banner("coin", "سکه امامی", data['coin_emami'])
        input_file = BufferedInputFile(photo_bytes.read(), filename="coin.png")
        await message.reply_photo(photo=input_file, caption="🪙 قیمت لحظه‌ای سکه امامی (ریال)")

@dp.message(F.text.contains("طلا"))
async def group_gold_listener(message: types.Message):
    data = await get_market_data()
    if data and data['gold_18k'] != "نامشخص":
        photo_bytes = generate_price_banner("gold", "طلای 18 عیار (هر گرم)", data['gold_18k'])
        input_file = BufferedInputFile(photo_bytes.read(), filename="gold.png")
        await message.reply_photo(photo=input_file, caption="🥇 قیمت لحظه‌ای طلای ۱۸ عیار (ریال)")

async def main() -> None:
    logging.basicConfig(level=logging.INFO)
    print("صراف‌باشی در حال اجراست... (Bot is starting...)")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())