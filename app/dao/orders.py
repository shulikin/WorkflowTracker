from app.dao.base import BaseDAO
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from app.models.models import Orders
from sqlalchemy.ext.asyncio import AsyncSession


class OrdersDAO(BaseDAO[Orders]):
    model = Orders

    def __init__(self, session: AsyncSession):
        self._session = session

    async def find_all(self):
        result = await self._session.execute(
            select(self.model).options(joinedload(Orders.clients))
        )
        return result.scalars().all()
