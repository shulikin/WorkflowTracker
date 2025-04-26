from fastapi import APIRouter, Form, Request, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.templates import templates
from app.dao.position import PositionDAO
from app.dependencies.auth_dep import get_current_user
from app.dao.database import get_session
from app.models.models import User
from app.schemas.position import PositionCreate

router = APIRouter()


@router.get("/positions/")
async def positions_page(
    request: Request,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user)
):
    positions = await PositionDAO(session).find_all()
    return templates.TemplateResponse("positions/positions.html", {
        "user": user,
        "request": request,
        "positions": positions,
    })


@router.post("/position/create")
async def create_position(
    name: str = Form(...),
    session: AsyncSession = Depends(get_session),
):
    position_data = PositionCreate(
        name=name,
    )
    await PositionDAO(session).add(position_data)
    return RedirectResponse(url="/positions", status_code=303)


@router.post("/position/{position_id}/edit")
async def edit_position(
    position_id: int,
    name: str = Form(...),
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user)
):
    position = await PositionDAO(session).find_one_or_none_by_id(position_id)
    if not position:
        return RedirectResponse(url="/positions", status_code=404)

    position.name = name
    await session.commit()
    return RedirectResponse(url="/positions", status_code=303)


# @router.get("/position/{position_id}")
# async def get_position_by_id(
#     position_id: int,
#     request: Request,
#     session: AsyncSession = Depends(get_session),
#     user: User = Depends(get_current_user)
# ):
#     position = await PositionDAO(session).find_one_or_none_by_id(position_id)
#     if not position:
#         return templates.TemplateResponse("404.html", {
#             "request": request,
#             "user": user,
#             "message": "Клиент не найден",
#         }, status_code=404)

#     return templates.TemplateResponse("positions/position_detail.html", {
#         "request": request,
#         "user": user,
#         "position": position,
#     })


@router.post("/position/{position_id}/delete")
async def delete_position(
    position_id: int,
    session: AsyncSession = Depends(get_session),
):
    position = await PositionDAO(session).find_one_or_none_by_id(position_id)
    if position:
        await session.delete(position)
        await session.commit()
    return RedirectResponse(url="/positions", status_code=303)
