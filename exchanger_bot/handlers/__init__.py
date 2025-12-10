from aiogram import Router

from handlers.exchange_menu import get_exchange_menu_router
from handlers.start import get_start_router
from handlers.user_menu import get_user_menu_router


def get_full_router() -> Router:
    """Создает и возвращает роутер для пользовательских команд."""
    router = Router()
    router.include_router(get_start_router())
    router.include_router(get_exchange_menu_router())
    router.include_router(get_user_menu_router())

    return router
