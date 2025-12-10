import os

import aiohttp
from dotenv import load_dotenv


load_dotenv()
API_KEY = os.getenv('EXCHANGER_API_KEY')


class Exchanger:
    base_url = f'https://v6.exchangerate-api.com/v6/{API_KEY}'

    @classmethod
    async def get_currency(cls, base_currency: str, target_currency: str):
        url = f"{cls.base_url}/pair/{base_currency}/{target_currency}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()

                    # Проверяем успешность запроса в JSON
                    if data.get('result') == 'success':
                        conversion_rate = data.get('conversion_rate')
                        return conversion_rate
                    else:
                        error_type = data.get('error-type', 'Unknown error')
                        raise Exception(f"API error: {error_type}")
                else:
                    response.raise_for_status()

