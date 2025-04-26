from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import Orders
from app.schemas.orders import OrderCreate


# Универсальная функция для получения всех записей в таблице
async def get_all_records(table, session: AsyncSession):
    result = await session.execute(select(table))
    return result.scalars().all()


async def create_order_in_db(order_data: OrderCreate, session: AsyncSession) -> Orders:
    db_order = Orders(**order_data.model_dump())
    session.add(db_order)
    await session.commit()
    await session.refresh(db_order)
    return db_order
