from aiogram.types import InlineKeyboardButton, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder 

from database import request as rq


def admin_btns(btns):
    kb = ReplyKeyboardBuilder()
    for text in btns:
        kb.add(KeyboardButton(text=text))
    return kb.adjust(2).as_markup(resize_keyboard=True, input_field_placeholder=('Выберите дествие снизу...'), one_time_keyboard=True)


async def admin_category():
    kb = InlineKeyboardBuilder()
    categories = await rq.get_categories()

    for category in categories:
        kb.add(InlineKeyboardButton(text=category.name, callback_data=f'edit_product_cat_{category.id}'))
    return kb.adjust(2).as_markup(one_time_keyboard=True)


async def edit_btns(product_id):
    kb=InlineKeyboardBuilder()
    kb.add(InlineKeyboardButton(text='Редактировать', callback_data=f'product_for_edit_{product_id}'))
    kb.add(InlineKeyboardButton(text='Удалить', callback_data=f'product_for_delete_{product_id}'))
    return kb.adjust(2).as_markup()


async def edit_cats_btns(category_id):
    kb = InlineKeyboardBuilder()
    kb.add(InlineKeyboardButton(text='Редактировать', callback_data=f'old_category_for_edit_{category_id}'))
    kb.add(InlineKeyboardButton(text='Удалить', callback_data=f'category_for_delete_{category_id}'))
    return kb.adjust(2).as_markup()