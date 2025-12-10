from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def get_menu_kb():
    inline_kb = [
        [
          InlineKeyboardButton(text='💰Пополнить баланс', callback_data='balance_add_menu')
        ],
        [
          InlineKeyboardButton(text='💸Вывести средства', callback_data='balance_out_menu')
        ],
        [
            InlineKeyboardButton(text='💹Курсы валют', callback_data='get_exchange_rate_menu')
        ],
        [
            InlineKeyboardButton(text='❤️Избранные пары', callback_data=f'get_fav_pirs')
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_kb)


def get_back_button_kb():
    inline_kb = [
        [
            InlineKeyboardButton(text='↩️Назад в меню', callback_data='back_button')
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_kb)


def get_pairs_kb():
    inline_kb = [
        [
            InlineKeyboardButton(text='🇺🇸RUB/USD', callback_data='get_pair_rub_usd'),
            InlineKeyboardButton(text='🇪🇺RUB/EUR', callback_data='get_pair_rub_eur'),
            InlineKeyboardButton(text='🇬🇧RUB/GBP', callback_data='get_pair_rub_gbp')
        ],
        [
            InlineKeyboardButton(text='🇨🇳RUB/CNY', callback_data='get_pair_rub_cny'),
            InlineKeyboardButton(text='🇯🇵RUB/JPY', callback_data='get_pair_rub_jpy'),
            InlineKeyboardButton(text='🇸🇬RUB/SGD', callback_data='get_pair_rub_sgd')
        ],
        [
            InlineKeyboardButton(text='🇦🇺RUB/AUD', callback_data='get_pair_rub_aud'),
            InlineKeyboardButton(text='🇦🇪RUB/AED', callback_data='get_pair_rub_aed'),
            InlineKeyboardButton(text='🇮🇳RUB/INR', callback_data='get_pair_rub_inr')
        ],
        [
            InlineKeyboardButton(text='↩️Назад в меню', callback_data='back_button')
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_kb)


def buy_currency_kb(target_currency: str, currency_rate: float):
    inline_kb = [
        [
            InlineKeyboardButton(text='➕Купить',
                                 callback_data=f'currency_operation_buy_{target_currency}:{currency_rate}')
        ],
        [
            InlineKeyboardButton(text='➖Продать',
                                 callback_data=f"currency_operation_sell_{target_currency}:{currency_rate}")
        ],
        [
            InlineKeyboardButton(text='↩️Назад в меню', callback_data='back_button')
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_kb)
