from aiogram import Dispatcher, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from .config import ADMIN_IDS
from .db import get_last_forms
from aiogram.types import FSInputFile
from .db import export_forms_to_csv

from .keyboards import main_menu_kb, back_kb, form_nav_kb
from .states import Form
from .db import save_form
async def ask_current_question(message_or_call, state: FSMContext):
    """Показываем нужный вопрос в зависимости от текущего состояния."""
    current = await state.get_state()

    if current == Form.name.state:
        text = "1/4 Как тебя зовут?"
    elif current == Form.age.state:
        text = "2/4 Сколько тебе лет? (числом)"
    elif current == Form.city.state:
        text = "3/4 Из какого ты города?"
    elif current == Form.goal.state:
        text = "4/4 Зачем тебе бот/чему хочешь научиться? (коротко)"
    else:
        text = "Вопрос не найден 🤔"

    # message_or_call может быть Message или CallbackQuery
    if isinstance(message_or_call, CallbackQuery):
        await message_or_call.message.answer(text, reply_markup=form_nav_kb())
    else:
        await message_or_call.answer(text, reply_markup=form_nav_kb())


def register_handlers(dp: Dispatcher):

    @dp.message(CommandStart())
    async def start(message: Message, state: FSMContext):
        await state.clear()
        await message.answer("Привет! Выбери действие 👇", reply_markup=main_menu_kb())

    @dp.message(Command("myid"))
    async def myid(message: Message):
        await message.answer(f"Твой ID: {message.from_user.id}")

    @dp.message(Command("forms"))
    async def forms(message: Message):
        if not ADMIN_IDS:
            await message.answer("Админы не настроены. Добавь ADMIN_IDS в .env")
            return

        if message.from_user.id not in ADMIN_IDS:
            await message.answer("Нет доступа ❌")
            return

        rows = get_last_forms(limit=5)
        if not rows:
            await message.answer("Анкет пока нет.")
            return

        def clip(s: str, n: int) -> str:
            s = s.replace("\n", " ").strip()
            return s if len(s) <= n else s[: n - 1] + "…"

        parts = ["📋 Последние анкеты:\n"]
        for r in rows:
            username = f"@{r['username']}" if r["username"] else "(нет username)"
            parts.append(
                f"#{r['id']} | {r['created_at']}\n"
                f"user_id: {r['user_id']} {username}\n"
                f"Имя: {clip(r['name'], 40)}\n"
                f"Возраст: {r['age']}\n"
                f"Город: {clip(r['city'], 40)}\n"
                f"Цель: {clip(r['goal'], 300)}\n"
                "--------------------\n"
            )

        text = "".join(parts)

        MAX = 3900
        for i in range(0, len(text), MAX):
            await message.answer(text[i:i + MAX])


    @dp.callback_query(F.data == "hello")
    async def cb_hello(call: CallbackQuery):
        await call.answer()
        await call.message.answer("Привет! 👋", reply_markup=main_menu_kb())

    @dp.callback_query(F.data == "who")
    async def cb_who(call: CallbackQuery):
        await call.answer()
        await call.message.answer("Я твой Telegram-бот 🤖", reply_markup=main_menu_kb())

    @dp.callback_query(F.data == "help")
    async def cb_help(call: CallbackQuery):
        await call.answer()
        await call.message.answer(
            "Это раздел помощи.\n"
            "• Нажми кнопки в меню\n"
            "• Анкета задаст 4 вопроса\n",
            reply_markup=back_kb()
        )
    @dp.message(Command("help"))
    async def help_cmd(message: Message):
        await message.answer(
            "Команды:\n"
            "/start — меню\n"
            "/myid — твой Telegram ID\n"
            "/help — помощь\n\n"
            "Админ:\n"
            "/forms — последние анкеты\n"
            "/export — выгрузка анкет в CSV\n"
        )

    @dp.message(Command("export"))
    async def export_cmd(message: Message):
        if not ADMIN_IDS or message.from_user.id not in ADMIN_IDS:
            await message.answer("Нет доступа ❌")
            return

        filename = "forms_export.csv"
        count = export_forms_to_csv(filename)

        if count == 0:
            await message.answer("Анкет пока нет, нечего выгружать.")
            return

        await message.answer(f"Готово ✅ Записей: {count}. Отправляю файл…")
        await message.answer_document(FSInputFile(filename))

    @dp.callback_query(F.data == "back")
    async def cb_back(call: CallbackQuery, state: FSMContext):
        await call.answer()
        await state.clear()
        await call.message.answer("Главное меню 👇", reply_markup=main_menu_kb())

    # --- Анкета: старт ---
    @dp.callback_query(F.data == "form")
    async def cb_form(call: CallbackQuery, state: FSMContext):
        await call.answer()
        await state.clear()
        await state.set_state(Form.name)
        await ask_current_question(call, state)

    # --- Анкета: отмена ---
    @dp.callback_query(F.data == "form_cancel")
    async def cb_form_cancel(call: CallbackQuery, state: FSMContext):
        await call.answer("Отменено")
        await state.clear()
        await call.message.answer("Анкета отменена. Главное меню 👇", reply_markup=main_menu_kb())

    # --- Анкета: назад ---
    @dp.callback_query(F.data == "form_back")
    async def cb_form_back(call: CallbackQuery, state: FSMContext):
        await call.answer()

        current = await state.get_state()
        if current == Form.name.state:
            # уже на первом шаге — просто меню
            await state.clear()
            await call.message.answer("Главное меню 👇", reply_markup=main_menu_kb())
            return

        if current == Form.age.state:
            await state.set_state(Form.name)
        elif current == Form.city.state:
            await state.set_state(Form.age)
        elif current == Form.goal.state:
            await state.set_state(Form.city)

        await ask_current_question(call, state)

    # --- Шаг 1: имя ---
    @dp.message(Form.name)
    async def form_name(message: Message, state: FSMContext):
        name = (message.text or "").strip()
        if len(name) < 2:
            await message.answer("Имя слишком короткое. Напиши ещё раз 🙂", reply_markup=form_nav_kb())
            return

        await state.update_data(name=name)
        await state.set_state(Form.age)
        await ask_current_question(message, state)

    # --- Шаг 2: возраст ---
    @dp.message(Form.age)
    async def form_age(message: Message, state: FSMContext):
        text = (message.text or "").strip()
        if not text.isdigit():
            await message.answer("Возраст нужно написать числом 🙂", reply_markup=form_nav_kb())
            return

        age = int(text)
        if age < 6 or age > 120:
            await message.answer("Слишком странный возраст 🙂 Напиши реальный.", reply_markup=form_nav_kb())
            return

        await state.update_data(age=age)
        await state.set_state(Form.city)
        await ask_current_question(message, state)

    # --- Шаг 3: город ---
    @dp.message(Form.city)
    async def form_city(message: Message, state: FSMContext):
        city = (message.text or "").strip()
        if len(city) < 2:
            await message.answer("Город слишком короткий. Напиши ещё раз 🙂", reply_markup=form_nav_kb())
            return
        await state.update_data(city=city)
        await state.set_state(Form.goal)
        await ask_current_question(message, state)
    # --- Шаг 4: цель + итог ---
    @dp.message(Form.goal)
    async def form_goal(message: Message, state: FSMContext):
        goal = (message.text or "").strip()
        if len(goal) < 3:
            await message.answer("Слишком коротко 🙂 Напиши чуть подробнее.", reply_markup=form_nav_kb())
            return
        await state.update_data(goal=goal)
        data = await state.get_data()
        await state.clear()
        save_form(
            user_id=message.from_user.id,
            username=message.from_user.username,
            name=data.get("name"),
            age=data.get("age"),
            city=data.get("city"),
            goal=data.get("goal"),
        )
        summary = (
            "✅ Анкета заполнена!\n\n"
            f"Имя: {data.get('name')}\n"
            f"Возраст: {data.get('age')}\n"
            f"Город: {data.get('city')}\n"
            f"Цель: {data.get('goal')}\n"
        )
        await message.answer(summary, reply_markup=main_menu_kb())
