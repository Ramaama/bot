from aiogram.utils.keyboard import InlineKeyboardBuilder

def main_menu_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="👋 Привет", callback_data="hello")
    kb.button(text="🤖 Кто ты", callback_data="who")
    kb.button(text="❓ Помощь", callback_data="help")
    kb.button(text="📝 Анкета", callback_data="form")
    kb.adjust(2, 1, 1)
    return kb.as_markup()

def back_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="⬅️ Назад", callback_data="back")
    return kb.as_markup()

def form_nav_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="⬅️ Назад", callback_data="form_back")
    kb.button(text="❌ Отмена", callback_data="form_cancel")
    kb.adjust(2)
    return kb.as_markup()
