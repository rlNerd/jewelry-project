from aiogram.types import InputMediaPhoto

from kbds import inline as kb
from database import request as rq

from utils.paginator import Paginator


async def main_menu(level, menu_name):
    banner = await rq.get_banner(menu_name)
    image = InputMediaPhoto(media = banner.image, caption=banner.description)

    kbds = kb.get_user_main_btns(level=level, size=(2,3,1))

    return image, kbds


async def category_list(level, menu_name):
    banner = await rq.get_banner(menu_name)
    image = InputMediaPhoto(media=banner.image, caption=banner.description)

    kbds = await kb.get_user_catalog_btns(level=level)

    return image, kbds


def pages(paginator:Paginator):
    btns = dict()
    if paginator.has_prev():
        btns['⬅️'] = 'prev'

    if paginator.has_next():
        btns['➡️'] = 'next'
    
    return btns


async def product_menu(level, category_id, page):
    products = await rq.get_products(category_id)

    paginator = Paginator(products, page=page)
    product = paginator.get_page()[0]
    image = InputMediaPhoto(
        media=product.image, 
        caption=f'<b>{product.name}</b>\
                \n\n<b>Описание:</b>\n{product.description}\
                \n\n<b>Стоимость: {product.price}</b>\
                \n\n<b>Товар {paginator.page} из {paginator.len}</b>',)
    
    paginator_btns = pages(paginator)
    kbds = kb.get_user_product_btns(level=level, category_id=category_id, page=page,
                                           paginator_btns=paginator_btns, product_id=product.id)

    return image,kbds


async def questions_menu(level, menu_name, page):
    questions = await rq.get_questions()

    q_paginator = Paginator(questions, page=page)
    question = q_paginator.get_page()[0]
    image = InputMediaPhoto(media=question.image,
                            caption=f'\n<b>Вопрос {q_paginator.page} из {q_paginator.pages}</b>\
                            \n\n{question.description}',

    )
    paginator_btns = pages(q_paginator)
    kbds = kb.get_user_questions_btns(level=level,
                                             page=page,
                                             paginator_btns=paginator_btns,)
    
    return image,kbds


async def busket_menu(level, menu_name, page, user_id, product_id):
    if menu_name == 'delete':
        await rq.delete_all_type_product(user_id, product_id) 
        if page > 1:
            page -= 1
    elif menu_name == 'del_one':
        is_busket = await rq.del_one_busket(user_id, product_id)
        if page > 1 and not is_busket:
            page -= 1
    elif menu_name == 'add_one':
        await rq.add_to_busket(user_id, product_id)

    buskets = await rq.get_user_busket(user_id) 

    if not buskets:
        banner = await rq.get_banner('busket')
        image = InputMediaPhoto(media=banner.image, caption=banner.description)
        kbds = kb.get_user_busket_btns(level=level,paginator_btns=None,product_id=None,page=None)
    
    else:
        paginator = Paginator(buskets,page=page)

        busket = paginator.get_page()[0]
        busket_price = busket.quantity * busket.product.price
        busket_total_price = sum(busket.quantity * busket.product.price for busket in buskets)

        image = InputMediaPhoto(media=busket.product.image,
                            caption=f'<b>{busket.product.name}</b>\n{busket.product.price}₽ * {busket.quantity} = {busket_price}₽\
                            \n<b>Товар {paginator.page} из {paginator.pages} в корзине</b>\nОбщая стоимость корзины: {busket_total_price}₽'
                            )
        pagination_btns = pages(paginator)

        kbds = kb.get_user_busket_btns(level=level,paginator_btns=pagination_btns,product_id=busket.product.id,page=page)

    return image, kbds


async def get_menu_content(
        level: int,
        menu_name: str,
        category_id: int | None = None,
        page: int = 1,
        product_id: int | None = None,
        user_id: int | None = None,
    ):

    if level == 0:
        return await main_menu(level, menu_name)
    if level == 1:
        return await category_list(level, menu_name)
    if level == 2:
        return await product_menu(level, category_id, page)
    if level == 3:
        return await busket_menu(level, menu_name, page, user_id, product_id)
    if level == 4:
        return await questions_menu(level, menu_name, page)