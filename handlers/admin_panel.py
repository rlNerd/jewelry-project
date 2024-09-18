from aiogram import F, Router
from aiogram.filters import Command, StateFilter, or_f
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from utils.chat_type import ChatTypeFilter, IsAdmin
from kbds import admin_kb as kb
from database import request as rq




admin_router = Router()
admin_router.message.filter(ChatTypeFilter(['private']), IsAdmin())


ADMIN_BTNS = [
    'Добавить товар',
    'Редактировать товар',
    'Добавить категорию',
    'Редактировать категорию',
    'Просто так зашел посмотреть', 
]


class AddProduct(StatesGroup):
    name = State()
    description = State()
    price = State()
    category = State()
    image = State()

    edited_product = None

    state_desc ={
        'AddProduct:name':'Введите название заново',
        'AddProduct:description':'Введите описание заново',
        'AddProduct:price':'Введите стоимость заново',
        'AddProduct:category':'Выберите категорию заново',
        'AddProduct:image':'-',
    }


@admin_router.message(Command('admin'))
async def admin_panel(message: Message):
    await message.answer('Открыта панель администратора, что вы хотите сделать?', reply_markup=kb.admin_btns(ADMIN_BTNS))


# FSM'ка на редактирование товара
@admin_router.message(F.text == 'Редактировать товар')  
async def edit_product(message: Message):
    await message.answer('Если вы не хотете менять какой-то параметр товара\nвведите " . " (точку)')
    await message.answer('Выберите категорию',reply_markup=await kb.admin_category())


@admin_router.message(F.text == 'Просто так зашел посмотреть')
async def back(message: Message):
    from handlers.user import cmd_start
    await cmd_start(message)




@admin_router.callback_query(F.data.startswith('edit_product_cat_'))  
async def edit_product2(callback: CallbackQuery):
    cat_id = int(callback.data.split('_')[-1])
    products = await rq.get_products(cat_id)

    for product in products:
        await callback.message.answer_photo(photo=product.image,
                                            caption=f'<b>{product.name}</b>\
                                            \n\n<b>Описание:</b>\n{product.description}\
                                            \n\n<b>Стоимость: {product.price}</b>'
                                            ,reply_markup=await kb.edit_btns(product.id))
        await callback.answer()


@admin_router.callback_query(StateFilter(None), F.data.startswith('product_for_edit_'))
async def edit_product3(callback: CallbackQuery, state: FSMContext):
    product_id = int(callback.data.split('_')[-1])
    edited_product = await rq.get_product(product_id)
    
    AddProduct.edited_product = edited_product
    
    await callback.answer()
    await callback.message.answer('Введите название модели',)
    await state.set_state(AddProduct.name)


@admin_router.callback_query(StateFilter(None), F.data.startswith('product_for_delete_'))
async def del_product(callback: CallbackQuery):
    del_id = int(callback.data.split('_')[-1])
    await rq.del_product(del_id)
    await callback.message.answer('Товар успешно удален 👍')
    await callback.answer()


# FSM'ка на добавление товара
@admin_router.message(StateFilter(None), F.text == 'Добавить товар')  
async def add_product(message: Message, state: FSMContext):
    await message.answer('Введите название товара')
    await state.set_state(AddProduct.name)


#ОТМЕНА
@admin_router.message(StateFilter('*'), Command('отмена'))
@admin_router.message(StateFilter('*'), F.text.lower() == 'отмена')
async def cancel_fsm(message: Message, state: FSMContext):
    check_state = await state.get_state()
    if check_state is None:
        return
    await state.clear()
    await message.answer('Отмена',reply_markup=kb.admin_btns(ADMIN_BTNS))


#НАЗАД
@admin_router.message(StateFilter('*'), Command('назад'))
@admin_router.message(StateFilter('*'), F.text.lower() == 'назад')
async def step_back(message: Message, state: FSMContext):
    check_state = await state.get_state()
    if check_state == AddProduct.name:
        await message.answer('Предыдущего шага нет.\nВведите название или напишите "отмена"')
        return
    
    prev = None
    for step in AddProduct.__all_states__:
        if step.state == check_state:
            await state.set_state(prev)
            await message.answer(f'Вы успешно вернулись к предыдущему шагу,\n{AddProduct.state_desc[prev.state]}')
        prev = step


@admin_router.message(StateFilter(AddProduct.name), F.text)  
async def add_product(message: Message, state: FSMContext):
    if message.text == '.':
        await state.update_data(name = AddProduct.edited_product.name)
    else:
        await state.update_data(name = message.text)
    await message.answer('Напишите описание товара')
    await state.set_state(AddProduct.description)


@admin_router.message(StateFilter(AddProduct.name))
async def add_name2(message: Message):
    await message.answer('Данные введены некорректно,\nвведите название товара заново')


@admin_router.message(StateFilter(AddProduct.description), F.text)  
async def add_product(message: Message, state: FSMContext):
    if message.text == '.':
        await state.update_data(description = AddProduct.edited_product.description)
    else:
        await state.update_data(description = message.text)
    await message.answer('Введите стоимость товара')
    await state.set_state(AddProduct.price)


@admin_router.message(StateFilter(AddProduct.description))
async def add_name2(message: Message):
    await message.answer('Данные введены некорректно,\nвведите описание товара заново')


@admin_router.message(StateFilter(AddProduct.price), F.text)
async def add_product(message: Message, state: FSMContext):
    categories = await rq.get_categories()
    if message.text == '.':
        await state.update_data(price = AddProduct.edited_product.price)
    else:
        try:
            int(message.text)
        except ValueError:
            await message.answer('Стоимость введена некорректно')
            return
        await state.update_data(price = message.text)
    await message.answer(f'Выберите категорию товара, напишите цифру нужной категории\n\n{"\n".join(sorted([str(c.id) +' - ' + c.name for c in categories]))}')
    await state.set_state(AddProduct.category)


@admin_router.message(StateFilter(AddProduct.price))
async def add_name2(message: Message):
    await message.answer('Данные введены некорректно,\nвведите цену товара заново')


@admin_router.message(StateFilter(AddProduct.category), F.text)  
async def add_product(message: Message, state: FSMContext):
    if message.text == '.':
        await state.update_data(category = AddProduct.edited_product.category)
    else:
        try:
            int(message.text)
        except ValueError:
            await message.answer('Категория введена некорректно')
            return
        await state.update_data(category = message.text)
    await message.answer('Прикрепите фотографию товара')
    await state.set_state(AddProduct.image)


@admin_router.message(StateFilter(AddProduct.category))
async def add_name2(message: Message):
    await message.answer('Данные введены некорректно,\nвведите категорию товара заново')


@admin_router.message(StateFilter(AddProduct.image), or_f(F.photo, F.text == '.'))  
async def add_product(message: Message, state: FSMContext):
    if message.text and message.text == '.' and AddProduct.edited_product:
        await state.update_data(image = AddProduct.edited_product.image)
    else:
        await state.update_data(image = message.photo[-1].file_id)
    data = await state.get_data()
    if AddProduct.edited_product:
        await rq.edit_product(data, AddProduct.edited_product.id)
        await message.answer('Товар отредактирован успешно 👍')
    else:
        await rq.add_new_product(data)
        await message.answer('Товар добавлен успешно 👍')

    await state.clear()
    AddProduct.edited_product = None


@admin_router.message(StateFilter(AddProduct.image))
async def add_name2(message: Message):
    await message.answer('Данные введены некорректно,\nприкрепите изображение товара заново')


#Работа с категориями
class NewCategory(StatesGroup):
    category_name = State()

    category_for_edit = None


@admin_router.message(F.text == 'Добавить категорию')
async def add_category(message:Message, state:FSMContext):
    await message.answer('Введите название категории')
    await state.set_state(NewCategory.category_name)


@admin_router.message(F.text == 'Редактировать категорию')
async def edit_cat(message: Message):
    cats = await rq.get_categories()
    await message.answer('Выберите категорию:')
    for c in cats:
        await message.answer(f'{c.name}',reply_markup=await kb.edit_cats_btns(c.id))


@admin_router.callback_query(StateFilter(None), F.data.startswith('old_category_for_edit_'))
async def edit_category1(callback: CallbackQuery, state: FSMContext):
    cat_id = int(callback.data.split('_')[-1])
    category_for_edit = await rq.get_category(cat_id)
    NewCategory.category_for_edit = category_for_edit
    await callback.answer()
    await callback.message.answer('Введите новое название категории')
    await state.set_state(NewCategory.category_name)   


@admin_router.callback_query(F.data.startswith('category_for_delete_'))
async def edit_category1(callback: CallbackQuery,):
    cat_id = int(callback.data.split('_')[-1])
    await rq.del_category(cat_id)
    await callback.answer()
    await callback.message.answer('Категория успешно удалена 👍')


@admin_router.message(StateFilter(NewCategory.category_name), F.text)
async def add_category2(message:Message, state:FSMContext):
    await state.update_data(category_name = message.text)
    data = await state.get_data()
    if NewCategory.category_for_edit:
        await rq.edit_category(data,NewCategory.category_for_edit.id)
        await message.answer('Категория успешно отредактирована 👍')
    else:
        await rq.add_category(data)
        await message.answer('Категория успешно добавлена 👍')

    await state.clear()
    NewCategory.category_for_edit = None