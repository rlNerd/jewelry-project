from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery

from database import request as rq
from handlers.menu_processing import get_menu_content
from kbds import inline as kb
from kbds.inline import MenuCallBack
from handlers.admin_panel import ADMIN_BTNS as ad_btns


user_router = Router()


@user_router.message(CommandStart())
async def cmd_start(message: Message):
    media, reply_markup = await get_menu_content(level=0, menu_name='main')
    user = message.from_user
    await rq.set_user_db(user.id, user.first_name, user.last_name, 0)
    await message.answer_photo(media.media, caption=media.caption, reply_markup=reply_markup)


async def add_to_busket(callback: CallbackQuery, callback_data: MenuCallBack):
    user = callback.from_user
    await rq.add_to_busket(user.id, product_id=callback_data.product_id,)
    await callback.answer('Товар добавлен в корзину')


@user_router.callback_query(MenuCallBack.filter())
async def user_menu(callback: CallbackQuery, callback_data: MenuCallBack):
    if callback_data.menu_name == 'add_to_busket':
        await add_to_busket(callback, callback_data)
        return

    media, reply_markup = await get_menu_content(
        level=callback_data.level,
        menu_name=callback_data.menu_name,
        category_id=callback_data.category,
        page=callback_data.page,
        product_id=callback_data.product_id,
        user_id=callback.from_user.id,
    )
    
    await callback.answer()
    await callback.message.edit_media(media=media, reply_markup=reply_markup)

# @user_router.message(F.photo)
# async def photo_id(message: Message):
#     await message.reply(message.photo[-1].file_id)
