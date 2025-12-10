from aiogram import Router
from aiogram.filters import CommandStart
from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from sqlalchemy import select

from data.database import AsyncSessionLocal
from config import bot
from data.models import User
from keyboards import inline


class Form(StatesGroup):
    msg_id = State()
    chat_id = State()


def get_start_router():
    router = Router()

    @router.message(CommandStart())
    async def handle_start(msg: types.Message, state: FSMContext):
        async with AsyncSessionLocal() as session:
            existing_user = await session.scalar(select(User).where(User.tg_id == msg.from_user.id))
            if not existing_user:
                new_user = User(
                    tg_id=msg.from_user.id,
                    chat_id=msg.chat.id,
                    first_name=msg.from_user.first_name
                )
                session.add(new_user)
                await session.commit()
            user = await session.scalar(select(User).where(User.tg_id == msg.from_user.id))
            text = f"Здравствуйте, {user.first_name}👋\n\n" \
                   f"❓Чем вам помочь\n\n" \
                   f"<b>💰ВАШИ СЧЕТА:\n" \
                   f"{user.balance_rub} RUB\n" \
                   f"{user.balance_usd} USD\n" \
                   f"{user.balance_eur} EUR\n" \
                   f"{user.balance_gbp} GBP\n" \
                   f"{user.balance_cny} CNY\n" \
                   f"{user.balance_jpy} JPY\n" \
                   f"{user.balance_sgd} SGD\n" \
                   f"{user.balance_aud} AUD\n" \
                   f"{user.balance_aed} AED\n" \
                   f"{user.balance_irn} IRN</b>"

            sent_message = await bot.send_message(chat_id=msg.chat.id,
                                                  text=text,
                                                  reply_markup=inline.get_menu_kb(),
                                                  parse_mode='HTML')
            await state.update_data(msg_id=sent_message.message_id)
            await state.update_data(chat_id=msg.chat.id)

    return router
