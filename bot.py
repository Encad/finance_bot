import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from database import add_expense, get_expenses, get_stats, clear_expenses

TOKEN = "7805259495:AAGJvs67aicqZanPYlDg0Bn6kqNHA9MrDCQ"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# FSM для добавления расхода
class AddExpenseStates(StatesGroup):
    waiting_amount = State()
    waiting_category = State()

# кнопки
keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="/add")],  # вот так теперь
        [KeyboardButton(text="/list"), KeyboardButton(text="/stats")],
        [KeyboardButton(text="/clear")]
    ],
    resize_keyboard=True
)

# /start
@dp.message(Command("start"))
async def start(msg: types.Message):
    await msg.answer(
        "Привет! Я бот для учета расходов 💸\n"
        "Используй кнопки ниже для управления расходами",
        reply_markup=keyboard
    )

# /add кнопка — запускаем FSM
@dp.message(Command("add"))
async def add_start(msg: types.Message, state: FSMContext):
    await msg.answer("Введите сумму расхода:")
    await state.set_state(AddExpenseStates.waiting_amount)

# получаем сумму
@dp.message(AddExpenseStates.waiting_amount)
async def add_amount(msg: types.Message, state: FSMContext):
    if not msg.text.isdigit():
        await msg.answer("Пожалуйста, введите число!")
        return
    await state.update_data(amount=int(msg.text))
    await msg.answer("Теперь введите категорию расхода:")
    await state.set_state(AddExpenseStates.waiting_category)

# получаем категорию и сохраняем
@dp.message(AddExpenseStates.waiting_category)
async def add_category(msg: types.Message, state: FSMContext):
    data = await state.get_data()
    amount = data["amount"]
    category = msg.text
    add_expense(msg.from_user.id, amount, category)
    await msg.answer(f"Записал расход: {amount} ₽ — {category}")
    await state.clear()  # очищаем FSM

# /list
@dp.message(Command("list"))
async def list_exp(msg: types.Message):
    expenses = get_expenses(msg.from_user.id)
    if not expenses:
        await msg.answer("Пока расходов нет")
        return

    text = "Твои расходы:\n"
    for amount, category, date in expenses:
        text += f"{date} — {amount} ₽ — {category}\n"

    await msg.answer(text)

# /stats с топ 3 категорий
@dp.message(Command("stats"))
async def stats(msg: types.Message):
    data = get_stats(msg.from_user.id)
    if not data:
        await msg.answer("Расходов пока нет")
        return

    # сортируем и берём топ 3
    data_sorted = sorted(data, key=lambda x: x[1], reverse=True)[:3]

    total = sum(item[1] for item in data)
    text = f"Всего потрачено: {total} ₽\n\nТоп 3 категории:\n"
    for category, amount in data_sorted:
        text += f"{category} — {amount} ₽\n"

    await msg.answer(text)

# /clear
@dp.message(Command("clear"))
async def clear(msg: types.Message):
    clear_expenses(msg.from_user.id)
    await msg.answer("Все расходы удалены 🗑️")

# запуск бота
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
