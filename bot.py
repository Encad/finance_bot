import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.filters.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram import F

from database import add_expense, clear_expenses, get_expenses, get_stats, get_total

# загружаем токен
load_dotenv()
TOKEN = os.getenv("TOKEN")
if TOKEN is None:
    raise ValueError("Токен не найден! Проверьте файл .env")

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# кнопки
keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="/add")],
        [KeyboardButton(text="/list"), KeyboardButton(text="/stats")],
        [KeyboardButton(text="/total"), KeyboardButton(text="/clear")],
        [KeyboardButton(text="/help")]
    ],
    resize_keyboard=True
)

# FSM для добавления расходов
class AddExpense(StatesGroup):
    waiting_for_category = State()
    waiting_for_amount = State()

# старт
@dp.message(Command(commands=["start"]))
async def start(msg: types.Message):
    await msg.answer("Привет! Я твой бот для учета расходов 💰", reply_markup=keyboard)

@dp.message(Command(commands=["help"]))
async def help_command(msg: types.Message):
    text = (
        "Команды:\n"
        "/add — добавить расход\n"
        "/list — последние 10 расходов\n"
        "/stats — топ категорий\n"
        "/total — всего потрачено\n"
        "/clear — очистить расходы\n"
        "/help — помощь"
    )
    await msg.answer(text)

# добавление через кнопку /add
@dp.message(Command(commands=["add"]))
async def add_command(msg: types.Message, state: FSMContext):
    await msg.answer("Напиши категорию расхода:")
    await state.set_state(AddExpense.waiting_for_category)

@dp.message(AddExpense.waiting_for_category)
async def category_received(msg: types.Message, state: FSMContext):
    category = msg.text.strip()
    if not category:
        await msg.answer("Категория не может быть пустой. Напиши категорию расхода:")
        return
    await state.update_data(category=category)
    await msg.answer("Теперь введи сумму расхода:")
    await state.set_state(AddExpense.waiting_for_amount)

@dp.message(AddExpense.waiting_for_amount)
async def amount_received(msg: types.Message, state: FSMContext):
    try:
        amount = float(msg.text.replace(",", "."))
    except ValueError:
        await msg.answer("Ошибка: введи число!")
        return
    if amount <= 0:
        await msg.answer("Сумма должна быть больше нуля.")
        return
    data = await state.get_data()
    category = data['category']
    add_expense(msg.from_user.id, amount, category)
    await msg.answer(f"Добавлено: {category} — {amount}₽")
    await state.clear()

# список расходов
@dp.message(Command(commands=["list"]))
async def list_exp(msg: types.Message):
    expenses = get_expenses(msg.from_user.id)
    if not expenses:
        await msg.answer("Нет расходов")
        return
    text = "Твои расходы:\n"
    for amount, category, date in expenses[:10]:
        text += f"{date[:16]} — {category}: {amount}₽\n"
    await msg.answer(text)

# топ 3 категорий
@dp.message(Command(commands=["stats"]))
async def stats(msg: types.Message):
    stats_data = get_stats(msg.from_user.id)
    if not stats_data:
        await msg.answer("Нет расходов")
        return
    total = get_total(msg.from_user.id)
    text = f"Топ 3 категории по расходам (всего {total}₽):\n"
    for cat, total in stats_data:
        text += f"{cat}: {total}₽\n"
    await msg.answer(text)

# всего
@dp.message(Command(commands=["total"]))
async def total(msg: types.Message):
    total_amount = get_total(msg.from_user.id)
    await msg.answer(f"Всего потрачено: {total_amount}₽")

# очистка базы
@dp.message(Command(commands=["clear"]))
async def clear(msg: types.Message):
    clear_expenses(msg.from_user.id)
    await msg.answer("Все расходы удалены.")

# запуск
if __name__ == "__main__":
    import asyncio
    asyncio.run(dp.start_polling(bot))
