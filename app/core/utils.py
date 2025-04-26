from fastapi import Request, HTTPException
from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession
from collections.abc import Sequence

from app.models.models import Process, Action


def redirect_or_raise(request: Request, exc: Exception):
    """Если accept: text/html или application/json — выбрасываем исключение.
    Иначе редиректим на login_page."""
    raise HTTPException(
        status_code=303,
        headers={"Location": str(request.url_for("login_page"))}
    )


class QueueService:
    def __init__(self, session: AsyncSession):
        self.session = session

    # Для процессов
    async def add_process_to_order(self, order_id: int) -> Process:
        max_queue = await self.session.scalar(
            select(func.max(Process.queue))
            .where(Process.order_id == order_id)
        )

        process = Process(
            order_id=order_id,
            queue=(max_queue or 0) + 1
        )

        self.session.add(process)
        await self.session.commit()
        return process

    async def get_order_processes(self, order_id: int) -> Sequence[Process]:
        result = await self.session.execute(
            select(Process)
            .where(Process.order_id == order_id)
            .order_by(Process.queue)
        )
        return result.scalars().all()

    # Для действий
    async def add_action_to_process(self, process_id: int) -> Action:
        max_queue = await self.session.scalar(
            select(func.max(Action.queue))
            .where(Action.process_id == process_id)
        )

        action = Action(
            process_id=process_id,
            queue=(max_queue or 0) + 1
        )

        self.session.add(action)
        await self.session.commit()
        return action

    async def get_process_actions(self, process_id: int) -> Sequence[Action]:
        result = await self.session.execute(
            select(Action)
            .where(Action.process_id == process_id)
            .order_by(Action.queue)
        )
        return result.scalars().all()

    async def move_process_in_order_queue(
        self,
        process_id: int,
        new_position: int
    ):
        process = await self.session.get(Process, process_id)
        if not process:
            raise ValueError("Process not found")

        await self._move_in_queue(
            model=Process,
            parent_id_attr="order_id",
            parent_id=process.order_id,
            current_pos=process.queue,
            new_pos=new_position,
            item_id=process_id
        )

    async def move_action_in_process_queue(
        self,
        action_id: int,
        new_position: int
    ):
        action = await self.session.get(Action, action_id)
        if not action:
            raise ValueError("Action not found")

        await self._move_in_queue(
            model=Action,
            parent_id_attr="process_id",
            parent_id=action.process_id,
            current_pos=action.queue,
            new_pos=new_position,
            item_id=action_id
        )

    async def _move_in_queue(
        self,
        model,
        parent_id_attr: str,
        parent_id: int,
        current_pos: int,
        new_pos: int,
        item_id: int
    ):
        if new_pos < 1:
            raise ValueError("Position must be positive")

        async with self.session.begin():
            # Получаем максимальную позицию
            max_pos = await self.session.scalar(
                select(func.max(model.queue))
                .where(getattr(model, parent_id_attr) == parent_id)
            )

            if (
                new_pos is not None
                and max_pos is not None
                and new_pos > max_pos
            ):
                new_pos = max_pos

            if current_pos == new_pos:
                return

            # Сдвигаем элементы
            if new_pos > current_pos:
                # Вниз
                await self.session.execute(
                    update(model)
                    .where(
                        (getattr(model, parent_id_attr) == parent_id) &
                        (model.queue > current_pos) &
                        (model.queue <= new_pos)
                    )
                    .values(queue=model.queue - 1)
                )
            else:
                # Вверх
                await self.session.execute(
                    update(model)
                    .where(
                        (getattr(model, parent_id_attr) == parent_id) &
                        (model.queue >= new_pos) &
                        (model.queue < current_pos)
                    )
                    .values(queue=model.queue + 1)
                )

            # Устанавливаем новую позицию
            await self.session.execute(
                update(model)
                .where(model.id == item_id)
                .values(queue=new_pos)
            )
