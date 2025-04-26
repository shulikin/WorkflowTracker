from fastapi import APIRouter, Form, Request, Depends
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from app.auth.dao import UsersDAO
from app.core.templates import templates
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import User
from app.dependencies.dao_dep import get_session_without_commit
from app.auth.utils import authenticate_user, set_tokens
from app.schemas.auth import EmailModel
from app.dependencies.auth_dep import get_current_user, get_refresh_token
from app.auth.utils import redirect_to_login

router = APIRouter()


@router.get("/")
async def home_page(
    request: Request,
    token: str = Depends(get_refresh_token),
    user: User = Depends(get_current_user),
):
    if not token:
        return RedirectResponse(url="/login")
    print(user)
    context = {
        "user": user,
        "request": request,  # ОБЯЗАТЕЛЬНО!
        "message": "Добро пожаловать! Вы авторизованы!",
    }
    accept_header = request.headers.get("accept", "")
    if "application/json" in accept_header:
        return JSONResponse(content={"message": context["message"]})
    return templates.TemplateResponse("protected.html", context)


@router.get("/login", name="login_page")
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login")
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    session: AsyncSession = Depends(get_session_without_commit)
):
    users_dao = UsersDAO(session)
    user = await users_dao.find_one_or_none(filters=EmailModel(email=username))
    if not (user and await authenticate_user(user=user, password=password)):
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Неправильный логин или пароль"
        })
    response = redirect_to_login(request, "home_page")
    set_tokens(response, user.id)
    return response


@router.get("/logout")
async def logout(request: Request):
    response = redirect_to_login(request, "login_page")
    response.delete_cookie("user_access_token", path="/")
    response.delete_cookie("user_refresh_token", path="/")
    return response
