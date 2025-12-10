from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from sqlalchemy import select

from data.database import AsyncSessionLocal
from config import bot
from data.models import User
from keyboards import inline
from services.exchanger_service import Exchanger


class Form(StatesGroup):
    msg_id = State()
    chat_id = State()
    currency_rate = State()
    currency = State()
    amount = State()
    max_amount = State()


def get_exchange_menu_router():
    router = Router()

    @router.callback_query(F.data == 'get_exchange_rate_menu')
    async def handle_exchange_menu(callback: types.CallbackQuery):
        msg_id = callback.message.message_id
        chat_id = callback.message.chat.id
        text = '❓Выберите нужную пару:'
        await bot.edit_message_text(text=text, chat_id=chat_id,
                                    message_id=msg_id, reply_markup=inline.get_pairs_kb())

    @router.callback_query(F.data.startswith('get_pair_rub_'))
    async def handle_pair(callback: types.CallbackQuery, state: FSMContext):
        msg_id = callback.message.message_id
        chat_id = callback.message.chat.id
        text = ''
        currency_emoji = ''
        base_currency = 'RUB'
        target_currency = ''
        if callback.data == 'get_pair_rub_usd':
            target_currency = 'USD'
            currency_emoji = '💵'
        if callback.data == 'get_pair_rub_eur':
            target_currency = 'EUR'
            currency_emoji = '💶'
        if callback.data == 'get_pair_rub_gbp':
            target_currency = 'GBP'
            currency_emoji = '💷'
        if callback.data == 'get_pair_rub_cny':
            target_currency = 'CNY'
        if callback.data == 'get_pair_rub_jpy':
            target_currency = 'JPY'
        if callback.data == 'get_pair_rub_sgd':
            target_currency = 'SGD'
        if callback.data == 'get_pair_rub_aud':
            target_currency = 'AUD'
        if callback.data == 'get_pair_rub_aed':
            target_currency = 'AED'
        if callback.data == 'get_pair_rub_irn':
            target_currency = 'IRN'


        currency_rate = await Exchanger.get_currency(base_currency=base_currency,
                                                     target_currency=target_currency)
        if currency_rate:
            text = f'❇️Текущий курс RUB/{target_currency}: {currency_rate}\n\n' \
                   f'То есть 1 {target_currency} = {round(1 / currency_rate, 2)} RUB'
            sent_msg = await bot.edit_message_text(text=text, chat_id=chat_id,
                                                   message_id=msg_id,
                                                   reply_markup=inline.buy_currency_kb(target_currency=target_currency,
                                                                                       currency_rate=currency_rate))
            await state.update_data(msg_id=sent_msg.message_id)
        else:
            text = '⚠️Что-то пошло не так'
            sent_msg = await bot.edit_message_text(text=text, chat_id=chat_id,
                                                   message_id=msg_id,
                                                   reply_markup=inline.buy_currency_kb(
                                                       target_currency=target_currency,
                                                   currency_rate=currency_rate))
            await state.update_data(msg_id=sent_msg.message_id)

    @router.callback_query(F.data.startswith('currency_operation_'))
    async def handle_currency_operation(callback: types.CallbackQuery, state: FSMContext):
        msg_id = callback.message.message_id
        chat_id = callback.message.chat.id
        text = ''
        async with AsyncSessionLocal() as session:
            user = await session.scalar(select(User).where(User.tg_id == callback.from_user.id))
            balance_rub = user.balance_rub
            balance_usd = user.balance_usd
            balance_eur = user.balance_eur
            balance_gbp = user.balance_gbp
            balance_cny = user.balance_cny
            balance_jpy = user.balance_jpy
            balance_sgd = user.balance_sgd
            balance_aud = user.balance_aud
            balance_aed = user.balance_aed
            balance_irn = user.balance_irn

            data_list = callback.data.split(':')
            data = data_list[0]
            currency_rate = data_list[1]
            max_amount = round(balance_rub * float(currency_rate), 2)
            currency = ''
            if data == 'currency_operation_buy_USD':
                currency = 'USD'
            if data == 'currency_operation_buy_EUR':
                currency = 'EUR'
            if data == 'currency_operation_buy_GBP':
                currency = 'GBP'
            if data == 'currency_operation_buy_CNY':
                currency = 'CNY'
            if data == 'currency_operation_buy_JPY':
                currency = 'JPY'
            if data == 'currency_operation_buy_SGD':
                currency = 'SGD'
            if data == 'currency_operation_buy_AUD':
                currency = 'AUD'
            if data == 'currency_operation_buy_AED':
                currency = 'AED'
            if data == 'currency_operation_buy_INR':
                currency = 'INR'
            text = f"⁉️ Напишите сколько {currency} хотите купить?\n\n" \
                   f"Доступно для покупки {max_amount} {currency}"
            sent_msg = await bot.edit_message_text(text=text, chat_id=chat_id,
                                                   message_id=msg_id,
                                                   reply_markup=inline.get_back_button_kb())
            await state.update_data(msg_id=sent_msg.message_id)
            await state.update_data(currency_rate=currency_rate)
            await state.update_data(currency=currency)
            await state.update_data(max_amount=max_amount)
            await state.set_state(Form.amount)

    @router.message(Form.amount)
    async def handle_currency_amount(msg: types.Message, state: FSMContext):
        msg_id = msg.message_id
        chat_id = msg.chat.id
        state_data = await state.get_data()
        sent_msg_id = state_data['msg_id']
        currency_rate = state_data['currency_rate']
        currency = state_data['currency']
        print(f"\n\n\nCURR - {currency}\n\n\n")
        max_amount = state_data['max_amount']
        try:
            amount = int(msg.text.strip())
            if amount and amount <= max_amount:
                async with AsyncSessionLocal() as session:
                    user = await session.scalar(select(User).where(User.tg_id == msg.from_user.id))
                    balance_rub = user.balance_rub
                    balance_usd = user.balance_usd
                    balance_eur = user.balance_eur
                    balance_gbp = user.balance_gbp
                    balance_cny = user.balance_cny
                    balance_jpy = user.balance_jpy
                    balance_sgd = user.balance_sgd
                    balance_aud = user.balance_aud
                    balance_aed = user.balance_aed
                    balance_irn = user.balance_irn
                    if currency == 'USD':
                        print(f"\n\nAMOUNT = {amount}\n\nBalance = {balance_usd}")
                        user.balance_usd = balance_usd + amount
                        await session.commit()
                    if currency == 'EUR':
                        user.balance_eur = balance_eur + amount
                        await session.commit()
                    if currency == 'GBP':
                        user.balance_gbp = balance_gbp + amount
                        await session.commit()
                    if currency == 'CNY':
                        user.balance_cny = balance_cny + amount
                        await session.commit()
                    if currency == 'JPY':
                        user.balance_jpy = balance_jpy + amount
                        await session.commit()
                    if currency == 'SGD':
                        user.balance_sgd = balance_sgd + amount
                        await session.commit()
                    if currency == 'AUD':
                        user.balance_aud = balance_aud + amount
                        await session.commit()
                    if currency == 'AED':
                        user.balance_aed = balance_aed + amount
                        await session.commit()
                    if currency == 'IRN':
                        user.balance_irn = balance_irn + amount
                        await session.commit()
                    rate = float(currency_rate)
                    user.balance_rub = round(balance_rub - (round(amount / rate, 2)))
                    await session.commit()

                    text = f"✅Обмен успешно произведен!"
                    await bot.delete_message(message_id=msg_id, chat_id=chat_id)
                    sent_msg = await bot.edit_message_text(text=text, chat_id=chat_id,
                                                           message_id=sent_msg_id,
                                                           reply_markup=inline.get_back_button_kb())
                    await state.update_data(msg_id=sent_msg.message_id)

        except Exception as e:
            print(f"\n\nERR - {e}\n\n")

    return router

