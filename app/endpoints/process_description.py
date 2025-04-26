from fastapi import APIRouter, Form, Request, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.templates import templates
from app.dao.process_description import ProcessDescriptionDAO
from app.dependencies.auth_dep import get_current_user
from app.dao.database import get_session
from app.models.models import User, Position
from app.schemas.process_description import ProcessDescriptionCreate

router = APIRouter()


@router.get("/process_description/")
async def process_description_page(
    request: Request,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user)
):
    process_description = await ProcessDescriptionDAO(session).find_all()
    position = await session.execute(select(Position).order_by(Position.name))
    position = position.scalars().all()
    return templates.TemplateResponse(
        "process_description/process_description.html", {
            "user": user,
            "request": request,
            "process_description": process_description,
            "position": position,
        })


@router.post("/process_description/create")
async def create_process_description(
    name: str = Form(...),
    position_id: int = Form(...),
    description: str = Form(...),
    session: AsyncSession = Depends(get_session),
):
    process_description_data = ProcessDescriptionCreate(
        name=name,
        position_id=position_id,
        description=description,
    )
    await ProcessDescriptionDAO(session).add(process_description_data)
    return RedirectResponse(url="/process_description", status_code=303)


@router.post("/process_description/{proc_desc_id}/edit")
async def edit_process_description(
    proc_desc_id: int,
    name: str = Form(...),

    description: str = Form(...),
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user)
):
    process_description = await (
        ProcessDescriptionDAO(session).find_one_or_none_by_id(proc_desc_id))
    if not process_description:
        return RedirectResponse(url="/process_description", status_code=404)

    process_description.name = name
    process_description.description = description
    await session.commit()
    return RedirectResponse(
        url="/process_description/", status_code=303)


@router.get("/process_description/{proc_desc_id}")
async def get_process_description_by_id(
    proc_desc_id: int,
    request: Request,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user)
):
    process_description = await (
        ProcessDescriptionDAO(session).find_one_or_none_by_id(proc_desc_id))
    if not process_description:
        return templates.TemplateResponse("404.html", {
            "request": request,
            "user": user,
            "message": "Клиент не найден",
        }, status_code=404)

    return templates.TemplateResponse(
        "process_description/process_description_detail.html", {
            "request": request,
            "user": user,
            "process_description": process_description,
        })


@router.post("/process_description/{proc_desc_id}/delete")
async def delete_process_description(
    proc_desc_id: int,
    session: AsyncSession = Depends(get_session),
):
    process_description = await (
        ProcessDescriptionDAO(session).find_one_or_none_by_id(proc_desc_id))
    if process_description:
        await session.delete(process_description)
        await session.commit()
    return RedirectResponse(url="/process_description", status_code=303)
