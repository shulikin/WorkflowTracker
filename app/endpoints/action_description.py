from fastapi import APIRouter, Form, Request, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.templates import templates
from app.dao.action_description import ActionDescriptionDAO
from app.dependencies.auth_dep import get_current_user
from app.dao.database import get_session
from app.models.models import User
from app.schemas.action_description import ActionDescriptionCreate

router = APIRouter()


@router.get("/action_description/")
async def action_description_page(
    request: Request,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user)
):
    action_description = await ActionDescriptionDAO(session).find_all()
    return templates.TemplateResponse("action_description/action_description.html", {
        "user": user,
        "request": request,
        "action_description": action_description,
    })


@router.post("/action_description/create")
async def create_action_description(
    name: str = Form(...),
    description: str = Form(...),
    session: AsyncSession = Depends(get_session),
):
    action_description_data = ActionDescriptionCreate(
        name=name,
        description=description
    )
    await ActionDescriptionDAO(session).add(action_description_data)
    return RedirectResponse(url="/action_description", status_code=303)


@router.post("/action_description/{act_desc_id}/edit")
async def edit_action_description(
    act_desc_id: int,
    name: str = Form(...),
    description: str = Form(...),
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user)
):
    action_description = await ActionDescriptionDAO(session).find_one_or_none_by_id(act_desc_id)
    if not action_description:
        return RedirectResponse(url="/action_description", status_code=404)

    action_description.name = name
    action_description.description = description
    await session.commit()
    return RedirectResponse(url=f"/action_description/{act_desc_id}", status_code=303)


@router.get("/action_description/{act_desc_id}")
async def get_action_description_by_id(
    act_desc_id: int,
    request: Request,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user)
):
    action_description = await ActionDescriptionDAO(session).find_one_or_none_by_id(act_desc_id)
    if not action_description:
        return templates.TemplateResponse("404.html", {
            "request": request,
            "user": user,
            "message": "Клиент не найден",
        }, status_code=404)

    return templates.TemplateResponse("action_description/action_description_detail.html", {
        "request": request,
        "user": user,
        "action_description": action_description,
    })


@router.post("/action_description/{act_desc_id}/delete")
async def delete_action_description(
    act_desc_id: int,
    session: AsyncSession = Depends(get_session),
):
    action_description = await ActionDescriptionDAO(session).find_one_or_none_by_id(act_desc_id)
    if action_description:
        await session.delete(action_description)
        await session.commit()
    return RedirectResponse(url="/action_description", status_code=303)
