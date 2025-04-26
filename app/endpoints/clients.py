from fastapi import APIRouter, Form, Request, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.templates import templates
from app.dao.clients import ClientsDAO
from app.dependencies.auth_dep import get_current_user
from app.dao.database import get_session
from app.models.models import User
from app.schemas.clients import ClientsCreate

router = APIRouter()


@router.get("/clients/")
async def clients_page(
    request: Request,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user)
):
    clients = await ClientsDAO(session).find_all()
    return templates.TemplateResponse("clients/clients.html", {
        "user": user,
        "request": request,
        "clients": clients,
    })


@router.post("/client/create")
async def create_clients(
    name: str = Form(...),
    description: str = Form(...),
    session: AsyncSession = Depends(get_session),
):
    clients_data = ClientsCreate(
        name=name,
        description=description
    )
    await ClientsDAO(session).add(clients_data)
    return RedirectResponse(url="/clients", status_code=303)


@router.post("/client/{client_id}/edit")
async def edit_client(
    client_id: int,
    name: str = Form(...),
    description: str = Form(...),
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user)
):
    client = await ClientsDAO(session).find_one_or_none_by_id(client_id)
    if not client:
        return RedirectResponse(url="/clients", status_code=404)

    client.name = name
    client.description = description
    await session.commit()
    return RedirectResponse(url=f"/client/{client_id}", status_code=303)


@router.get("/client/{client_id}")
async def get_client_by_id(
    client_id: int,
    request: Request,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user)
):
    client = await ClientsDAO(session).find_one_or_none_by_id(client_id)
    if not client:
        return templates.TemplateResponse("404.html", {
            "request": request,
            "user": user,
            "message": "Клиент не найден",
        }, status_code=404)

    return templates.TemplateResponse("clients/client_detail.html", {
        "request": request,
        "user": user,
        "client": client,
    })


@router.post("/client/{client_id}/delete")
async def delete_client(
    client_id: int,
    session: AsyncSession = Depends(get_session),
):
    client = await ClientsDAO(session).find_one_or_none_by_id(client_id)
    if client:
        await session.delete(client)
        await session.commit()
    return RedirectResponse(url="/clients", status_code=303)
