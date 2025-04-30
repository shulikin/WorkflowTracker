"""process monitor"""
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from loguru import logger

from app.auth.router import router as router_auth
from app.endpoints.start import router as router_start
from app.endpoints.clients import router as router_clients
from app.endpoints.orders import router as router_orders
from app.endpoints.position import router as router_position
from app.endpoints.process_description import router as router_process_description
from app.endpoints.action_description import router as router_action_description


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Управление жизненным циклом приложения."""
    logger.info("Инициализация приложения...")
    yield
    logger.info("Завершение работы приложения...")


def create_app() -> FastAPI:
    """
   Создание и конфигурация FastAPI приложения.

   Returns:
       Сконфигурированное приложение FastAPI
   """
    app = FastAPI(
        title="Стартовая сборка FastAPI",
        description=(
            "Стартовая сборка с интегрированной SQLAlchemy 2"
            "для разработки FastAPI приложений с продвинутой "
            "архитектурой, включающей авторизацию,"
            "аутентификацию и управление ролями пользователей.\n\n"
            "**Автор проекта**: Яковенко Алексей\n"
            "**Telegram**: https://t.me/PythonPathMaster"
        ),
        version="1.0.0",
        lifespan=lifespan,
    )

    # Настройка CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
    )

    # Монтирование статических файлов
    app.mount(
        '/static',
        StaticFiles(directory='app/static'),
        name='static'
    )

    # Регистрация роутеров
    register_routers(app)

    return app


def register_routers(app: FastAPI) -> None:
    """Регистрация роутеров приложения."""

    # Подключение роутеров
    app.include_router(
        router_start, tags=["start"])
    app.include_router(
        router_action_description, tags=["action_description"])
    app.include_router(
        router_orders, tags=["orders"])
    app.include_router(
        router_position, tags=["position"])
    app.include_router(
        router_process_description, tags=["process_description"])
    app.include_router(
        router_clients, tags=["clients"])
    # app.include_router(root_router, tags=["root"])
    app.include_router(
        router_auth, prefix='/auth', tags=['Auth'])



# Создание экземпляра приложения
app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000)
