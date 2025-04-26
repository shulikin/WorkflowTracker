from datetime import datetime
from sqlalchemy import select, desc
from fastapi import APIRouter, Form, Request, Depends
from sqlalchemy.orm import selectinload
from fastapi.responses import RedirectResponse
from app.auth.dao import UsersDAO
from app.core.templates import templates
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import User, Clients, Orders
from app.schemas.orders import OrderCreate
from app.dao.db import connection
from app.dao.database import async_session_maker
from app.dao.orders import OrdersDAO
from app.dao.clients import ClientsDAO
from app.auth.utils import authenticate_user, set_tokens
from app.schemas.auth import EmailModel
from app.dependencies.auth_dep import check_refresh_token, get_current_user 
from app.dao.database import get_session

router = APIRouter()


@router.get("/orders")
async def orders_page(
    request: Request,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user)
):
    result = await session.execute(
        select(Orders).options(selectinload(Orders.clients)).order_by(desc(Orders.id))
    )
    orders = result.scalars().all()

    clients = await session.execute(select(Clients).order_by(Clients.name))
    clients = clients.scalars().all()
    return templates.TemplateResponse("orders/orders.html", {
        "user": user,
        "request": request,
        "orders": orders,
        "clients": clients,
    })


@router.post("/order/create")
async def create_order(
    client_id: int = Form(...),
    description: str = Form(...),
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
):
    now = datetime.now()
    datetime_str = now.strftime('%Y%m%d%H%M%S')
    order_data = OrderCreate(
        client_id=client_id,
        user_id=user.id,
        number=int(datetime_str),
        description=description
    )
    await OrdersDAO(session).add(order_data)
    return RedirectResponse(url="/orders", status_code=303)


@router.get("/order/{order_id}")
async def get_order_by_id(
    order_id: int,
    request: Request,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user)
):
    order = await OrdersDAO(session).find_one_or_none_by_id(order_id)
    if not order:
        return templates.TemplateResponse("404.html", {
            "request": request,
            "user": user,
            "message": "Клиент не найден",
        }, status_code=404)

    return templates.TemplateResponse("orders/order_detail.html", {
        "request": request,
        "user": user,
        "order": order,
    })
