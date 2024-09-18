from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database import request as rq



class MenuCallBack(CallbackData, prefix="menu"):
    level: int
    menu_name: str
    category: int | None = None
    page: int = 1
    product_id: int | None = None



def get_user_main_btns(*,level:int, size: tuple[int] = (2,)):
    kb = InlineKeyboardBuilder()
    btns = {
        'Товары 💍':'catalog',
        'Корзина 🛒':'busket',
        'Кто ты? 🙃': 'about_me',
        'Оплата 💸': 'payment',
        'Доставка 🕊️':'delivery',
        'Частые вопросы ❓':'questions',
    }
    for text, menu_name in btns.items():
        if menu_name == 'catalog':
            kb.add(InlineKeyboardButton(text=text,callback_data=MenuCallBack(level = level+1, menu_name=menu_name).pack()))
        elif menu_name == 'busket':
            kb.add(InlineKeyboardButton(text=text, callback_data=MenuCallBack(level = 3, menu_name=menu_name).pack()))
        elif menu_name == 'questions':
            kb.add(InlineKeyboardButton(text=text, callback_data=MenuCallBack(level = 4, menu_name=menu_name).pack()))
        else:
            kb.add(InlineKeyboardButton(text=text, callback_data=MenuCallBack(level = level, menu_name=menu_name).pack()))
    return kb.adjust(*size).as_markup()


async def get_user_catalog_btns(*,level, size: tuple[int]=(2,)):
    kb = InlineKeyboardBuilder()
    kb.add(InlineKeyboardButton(text='На главную 🏡',callback_data=MenuCallBack(level=level-1, menu_name='main').pack()))

    categories = await rq.get_categories()
    for c in categories:
        kb.add(InlineKeyboardButton(text=c.name, callback_data=MenuCallBack(level=level+1, menu_name=c.name, category=c.id).pack()))

    return kb.adjust(1,2).as_markup()


def get_user_product_btns(*,level,size: tuple[int]=(2,), category_id, page, paginator_btns, product_id):
    kb = InlineKeyboardBuilder()
    
    kb.add(InlineKeyboardButton(text='Назад',callback_data=MenuCallBack(level=level-1, menu_name='catalog').pack()))
    kb.add(InlineKeyboardButton(text='В Корзину 🛒',callback_data=MenuCallBack(level=3, menu_name='add_to_busket', product_id=product_id).pack()))

    kb.adjust(*size)

    row = []

    for text, action in paginator_btns.items():
        if action == 'next':
            row.append(InlineKeyboardButton(text=text,
                                            callback_data=MenuCallBack(level=level,menu_name=action,category=category_id,page=page+1).pack()))
        elif action == 'prev':
            row.append(InlineKeyboardButton(text=text,
                                            callback_data=MenuCallBack(level=level,menu_name=action,category=category_id,page=page-1).pack()))
    return kb.row(*row).as_markup()


def get_user_questions_btns(*,level,size: tuple[int]=(2,),page, paginator_btns):
    kb = InlineKeyboardBuilder()

    kb.add(InlineKeyboardButton(text='На главную 🏡',callback_data=MenuCallBack(level=0, menu_name='main').pack()))
    kb.adjust(*size)
    
    row = []
    for text, action in paginator_btns.items():
        if action == 'next':
            row.append(InlineKeyboardButton(text=text,
                                            callback_data=MenuCallBack(level=level,menu_name=action, page=page+1).pack()))
        elif action == 'prev':
            row.append(InlineKeyboardButton(text=text,
                                            callback_data=MenuCallBack(level=level,menu_name=action, page=page-1).pack()))

    return kb.row(*row).as_markup()


def get_user_busket_btns(*,level:int, paginator_btns: dict | None, product_id: int | None, page: int | None, size: tuple[int]=(2,)):

    kb = InlineKeyboardBuilder()
    if page:
        kb.add(InlineKeyboardButton(text='➕',callback_data=MenuCallBack(level=level, menu_name='add_one', product_id=product_id,page=page).pack()))
        kb.add(InlineKeyboardButton(text='Удалить',callback_data=MenuCallBack(level=level, menu_name='delete', product_id=product_id,page=page).pack()))
        kb.add(InlineKeyboardButton(text='➖',callback_data=MenuCallBack(level=level, menu_name='del_one', product_id=product_id,page=page).pack()))
    
        kb.adjust(3)

        row = []

        for text, action in paginator_btns.items():
            if action == 'next':
                row.append(InlineKeyboardButton(text=text,
                                                callback_data=MenuCallBack(level=level,menu_name=action, page=page+1).pack()))  
            elif action == 'prev':
                row.append(InlineKeyboardButton(text=text,
                                            callback_data=MenuCallBack(level=level,menu_name=action, page=page-1).pack()))
        kb.row(*row)

    row2 = []
    row2.append(InlineKeyboardButton(text='На главную 🏡',
                    callback_data=MenuCallBack(level=0, menu_name='main').pack())),
    kb.row(*row2)

    return kb.as_markup()