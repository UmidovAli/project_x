
from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from sqlalchemy import select

from config import bot
from data.database import AsyncSessionLocal
from data.models import User
from keyboards import inline


class Form(StatesGroup):
    msg_id = State()
    chat_id = State()
    rub_payment_amount = State()
    balance_out_payment = State()


def get_user_menu_router():
    router = Router()

    @router.callback_query(F.data == 'back_button')
    async def handle_back_to_menu(callback: types.CallbackQuery):
        msg_id = callback.message.message_id
        chat_id = callback.message.chat.id
        async with AsyncSessionLocal() as session:
            user = await session.scalar(select(User).where(User.tg_id == callback.from_user.id))
            text = f"✅Мы в меню\n\n" \
                   f"❓Чем вам помочь\n\n" \
                   f"<b>💰Баланс RUB: {user.balance_rub}\n" \
                   f"💰Баланс USD: {user.balance_usd}\n" \
                   f"💰Баланс EUR: {user.balance_eur}\n" \
                   f"💰Баланс GBP: {user.balance_gbp}\n" \
                   f"💰Баланс CNY: {user.balance_cny}\n" \
                   f"💰Баланс JPY: {user.balance_jpy}\n" \
                   f"💰Баланс SGD: {user.balance_sgd}\n" \
                   f"💰Баланс AUD: {user.balance_aud}\n" \
                   f"💰Баланс AED: {user.balance_aed}\n" \
                   f"💰Баланс IRN: {user.balance_irn}\n</b>"
            await bot.edit_message_text(text=text, chat_id=chat_id,
                                        message_id=msg_id, reply_markup=inline.get_menu_kb(),
                                        parse_mode='HTML')

    @router.callback_query(F.data == 'balance_add_menu')
    async def handle_balance_add(callback: types.CallbackQuery, state: FSMContext):
        msg_id = callback.message.message_id
        chat_id = callback.message.chat.id
        text = '❇️Напишите сколько RUB хотите внести?(Например, 1000)'
        sent_msg = await bot.edit_message_text(text=text, chat_id=chat_id,
                                               message_id=msg_id,
                                               reply_markup=inline.get_back_button_kb())
        await state.update_data(msg_id=sent_msg.message_id)
        await state.set_state(Form.rub_payment_amount)

    @router.message(Form.rub_payment_amount)
    async def handle_rub_payment(msg: types.Message, state: FSMContext):
        msg_id = msg.message_id
        chat_id = msg.chat.id
        state_data = await state.get_data()
        sent_msg_id = state_data['msg_id']
        async with AsyncSessionLocal() as session:
            user = await session.scalar(select(User).where(User.tg_id == msg.from_user.id))
            balance_rub = user.balance_rub
            user.balance_rub = balance_rub + float(msg.text.strip())
            await session.commit()
            upd_user = await session.scalar(select(User).where(User.tg_id == msg.from_user.id))
            text = f"✅Пополнение вашего баланс(RUB) прошло успешно!\n\n" \
                   f"Актуальный баланс(RUB): {upd_user.balance_rub} RUB."
            await bot.delete_message(message_id=msg_id, chat_id=chat_id)
            sent_msg = await bot.edit_message_text(text=text, chat_id=chat_id,
                                                   message_id=sent_msg_id,
                                                   reply_markup=inline.get_back_button_kb())
            await state.update_data(msg_id=sent_msg.message_id)

    @router.callback_query(F.data == 'balance_out_menu')
    async def handle_balance_out(callback: types.CallbackQuery, state: FSMContext):
        msg_id = callback.message.message_id
        chat_id = callback.message.chat.id
        text = ''
        async with AsyncSessionLocal() as session:
            user = await session.scalar(select(User).where(User.tg_id == callback.from_user.id))
            if user.balance_rub > 0:
                text = f"❇️Напишите сколько RUB хотите вывести?(Например, 1000)\n\n" \
                       f"<b>Баланс RUB: {user.balance_rub} RUB</b>"
                await state.set_state(Form.balance_out_payment)
                sent_msg = await bot.edit_message_text(text=text, chat_id=chat_id,
                                                       message_id=msg_id,
                                                       reply_markup=inline.get_back_button_kb(),
                                                       parse_mode='HTML')
                await state.update_data(msg_id=sent_msg.message_id)
            else:
                text = '⚠️У вас нет RUB на балансе'
                await callback.answer(text=text, show_alert=True)

    @router.message(Form.balance_out_payment)
    async def handle_balance_out(msg: types.Message, state: FSMContext):
        msg_id = msg.message_id
        chat_id = msg.chat.id
        text = ''
        state_data = await state.get_data()
        sent_msg_id = state_data['msg_id']
        try:
            amount_out = int(msg.text.strip())
            async with AsyncSessionLocal() as session:
                user = await session.scalar(select(User).where(User.tg_id == msg.from_user.id))
                balance_rub = user.balance_rub
                if amount_out <= user.balance_rub:
                    user.balance_rub = balance_rub - amount_out
                    await session.commit()
                    text = f'✅{amount_out} RUB успешно списаны с баланса и отправлены по вашим реквизитам!'
                    sent_msg = await bot.edit_message_text(text=text, chat_id=chat_id,
                                                           message_id=sent_msg_id,
                                                           reply_markup=inline.get_back_button_kb())
                    await bot.delete_message(chat_id=chat_id, message_id=msg_id)
                    await state.update_data(msg_id=sent_msg.message_id)
        except:
            text = '⚠️ Введите число'
            sent_msg = await msg.answer(text=text, reply_markup=inline.get_back_button_kb())
            await state.update_data(msg_id=sent_msg.message_id)

    return router
