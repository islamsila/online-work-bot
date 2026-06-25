import asyncio
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from groq import Groq

# 1. token.env faylidan o'zgaruvchilarni yuklash
load_dotenv("token.env")
BOT_TOKEN = os.getenv("BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not BOT_TOKEN or not GROQ_API_KEY:
    raise ValueError("BOT_TOKEN yoki GROQ_API_KEY topilmadi. token.env faylini tekshiring.")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
groq_client = Groq(api_key=GROQ_API_KEY)


# --- FSM (Holatlar) ---
class JobPostState(StatesGroup):
    waiting_for_details = State()  # Ish beruvchi ma'lumot kiritishini kutish


# --- Klaviaturalar (Keyboards) ---
def get_main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💼 Ish beruvchiman", callback_data="role_employer")],
        [InlineKeyboardButton(text="💻 Frilanserman", callback_data="role_freelancer")]
    ])


def get_freelancer_webapp():
    # Bu yerga vaqtinchalik o'zingizning GitHub Pages yoki istalgan ishlaydigan HTTPS ssilkani qo'yishingiz mumkin
    web_app_url = "https://sizning-domen.com/mini_app.html" 
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔍 Ish qidirish (Mini App)", web_app=WebAppInfo(url=web_app_url))]
    ])


def get_review_keyboard(freelancer_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Yoqdi", callback_data=f"accept_{freelancer_id}"),
            InlineKeyboardButton(text="❌ Yoqmadi", callback_data=f"reject_{freelancer_id}")
        ]
    ])


# --- Handlerlar ---

@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(
        f"Assalomu alaykum, {message.from_user.first_name}!\nPlatformamizga xush kelibsiz. Kim bo'lib tizimga kirmoqchisiz?",
        reply_markup=get_main_menu()
    )


# 1. ROL TANLASH
@dp.callback_query(F.data.startswith("role_"))
async def role_selection(callback: CallbackQuery, state: FSMContext):
    role = callback.data.split("_")[1]

    if role == "employer":
        await callback.message.answer(
            "Sizga qanday mutaxassis kerak? Ish tavsifi, narxi va qayerdanligingizni bitta xabarda yozib yuboring.\n*(AI yordamida buni o'zimiz tartiblab olamiz)*")
        await state.set_state(JobPostState.waiting_for_details)

    elif role == "freelancer":
        await callback.message.answer("Quyidagi tugma orqali ilovaga kiring va o'zingizga mos ishni toping:",
                                      reply_markup=get_freelancer_webapp())

    await callback.answer()


# 2. ISH BERUVCHI MA'LUMOT KIRITISHI VA AI TARTIBLASHI
@dp.message(JobPostState.waiting_for_details)
async def process_job_details(message: Message, state: FSMContext):
    user_text = message.text

    # Bu yerda Groq AI yordamida matnni tizimlashtiramiz
    # Hozircha oddiy xabar qaytaramiz, keyin AI qismini to'liq ulaymiz
    await message.answer("Ma'lumotlaringiz qabul qilindi va bazaga saqlandi. Frilanserlar aloqaga chiqishini kuting!")
    await state.clear()


# 3. ISH BERUVCHI FRILANSERNI BAHOLASHI (Yoqdi / Yoqmadi)
@dp.callback_query(F.data.startswith("accept_") | F.data.startswith("reject_"))
async def review_freelancer(callback: CallbackQuery):
    action, freelancer_id = callback.data.split("_")

    if action == "accept":
        await callback.message.edit_text("Siz bu frilanserni qabul qildingiz! Unga xabar yuborildi.")
    else:
        await callback.message.edit_text("Siz bu frilanserni rad etdingiz.")

    await callback.answer()


async def main():
    print('Bot ishga tushdi...')
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
