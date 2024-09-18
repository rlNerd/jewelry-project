from database.models import User, Product, Category, Busket, Banner
from database.models import async_session

from sqlalchemy import delete, select, update
from sqlalchemy.orm import joinedload


async def set_user_db(tg_id, name, surname, status = 0):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))

        if not user:
            new_user = User(tg_id=tg_id, name=name,surname=surname, status=status)
            session.add(new_user)
            await session.commit()


async def get_banner(menu_name):
    async with async_session() as session:
        query = select(Banner).where(Banner.name == menu_name)
        res = await session.execute(query)
        return res.scalar()
    

async def get_categories():
    async with async_session() as session:
        query = select(Category)
        res = await session.execute(query)
        return sorted(res.scalars().all(),key=lambda x: x.id)


async def get_category(cat_id):
    async with async_session() as session:
        query = select(Category).where(Category.id == cat_id)
        res = await session.execute(query)
        return res.scalar()


#Вопросы
async def get_questions():
    async with async_session() as session:
        query = select(Banner).where(Banner.name == 'questions')
        res = await session.execute(query)
        return res.scalars().all()


#Товары
async def get_products(categoty_id):
    async with async_session() as session:
        query = select(Product).where(Product.category == categoty_id)
        res = await session.execute(query)
        return sorted(res.scalars().all(), key=lambda x: x.id)


async def get_product(product_id):
    async with async_session() as session:
        query = select(Product).where(Product.id == product_id)
        res = await session.execute(query)
        return res.scalar()


#Админка
async def check_adm_status(tg_id):
    async with async_session() as session:
        query = select(User).where(User.tg_id == tg_id)
        res = await session.execute(query)
        return res.scalar()
    
async def add_new_product(data):
    async with async_session() as session:
        new_product = Product(
            name=data['name'],
            description=data['description'],
            price=int(data['price']),
            category=int(data['category']),
            image=data['image'],
        )
        session.add(new_product)
        await session.commit()


async def edit_product(data, id):
    async with async_session() as session:
        edited_product=(update(Product).
                        where(Product.id == id).
                        values( name=data['name'],
                                description=data['description'],
                                price=int(data['price']),
                                category=int(data['category']),
                                image=data['image'],)
                        )
        await session.execute(edited_product)
        await session.commit()


async def del_product(product_id):
    async with async_session() as session:
        query = delete(Product).where(Product.id == product_id)
        await session.execute(query)
        await session.commit()


#Категории
async def add_category(data):
    async with async_session() as session:
        session.add(Category(name=data['category_name']))
        await session.commit()


async def edit_category(data, cat_id):
    async with async_session() as session:
        await session.execute(update(Category).
                              where(Category.id == cat_id).
                              values(name = data['category_name']))
        await session.commit()


async def del_category(cat_id):
    async with async_session() as session:
        query = delete(Category).where(Category.id == cat_id)
        await session.execute(query)
        await session.commit()


#Корзина
async def add_to_busket(user_id, product_id):
    async with async_session() as session:
        query = select(Busket).where(Busket.user_id == user_id, Busket.product_id == product_id)
        busket = await session.execute(query)
        busket = busket.scalar()
        if busket:
            busket.quantity +=1
            await session.commit()
            return busket
        else:
            session.add(Busket(user_id=user_id, product_id=product_id, quantity=1))
            await session.commit()


async def delete_all_type_product(user_id, product_id):
    async with async_session() as session:
        query = delete(Busket).where(Busket.user_id == user_id, Busket.product_id == product_id)
        await session.execute(query)
        await session.commit()

    
async def del_one_busket(user_id, product_id):
    async with async_session() as session:
        query = select(Busket).where(Busket.user_id == user_id, Busket.product_id == product_id)
        busket = await session.execute(query)
        busket = busket.scalar()

        if not busket:
            return
        if busket.quantity > 1:
            busket.quantity -= 1
            await session.commit()
            return True
        else:
            await delete_all_type_product(user_id, product_id)
            await session.commit()
            return False


async def get_user_busket(user_id):
    async with async_session() as session:
        query = select(Busket).where(Busket.user_id == user_id).options(joinedload(Busket.product))
        res = await session.execute(query)
        return res.scalars().all()