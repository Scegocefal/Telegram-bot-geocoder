import os
import logging
from urllib.parse import quote_plus
import json
from aiogram import Bot, Dispatcher, types, F
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from dotenv import load_dotenv
import requests

# Загрузка переменных окружения
load_dotenv('.env')

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

bot = Bot(token=os.getenv("TELEGRAM_TOKEN"))
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

class RouteStates(StatesGroup):
    waiting_for_location = State()
    waiting_for_address = State()

@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await message.answer("📍 Отправьте вашу геопозицию (нажмите на скрепку, далее 'Геопозиция').")
    await state.set_state(RouteStates.waiting_for_location)

@dp.message(
    F.content_type == "location",
    RouteStates.waiting_for_location
)
async def process_location(message: types.Message, state: FSMContext):
    await state.update_data(
        lat=message.location.latitude,
        lon=message.location.longitude
    )
    await message.answer("📬 Теперь введите адрес назначения в формате:\nГород, Улица дом\nПример: Москва, Арбат 15")
    await state.set_state(RouteStates.waiting_for_address)

@dp.message(RouteStates.waiting_for_address)
async def process_address(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    start_lat = user_data["lat"]
    start_lon = user_data["lon"]
    address = message.text.strip()

    try:
        # Логирование адреса
        logging.info(f"Получен адрес: {address}")

        # Кодирование адреса для URL
        formatted_address = quote_plus(address)
        geocoder_url = (
            f"https://geocode-maps.yandex.ru/1.x/?apikey={os.getenv('YANDEX_API_KEY')}"
            f"&geocode={formatted_address}&format=json"
        )
        logging.info(f"Запрос к API: {geocoder_url}")

        # Выполнение запроса
        response = requests.get(geocoder_url)
        response.raise_for_status()  # Проверка HTTP ошибок

        # Парсинг JSON
        data = response.json()
        logging.info(f"Ответ API:\n{json.dumps(data, indent=2, ensure_ascii=False)}")

        # Извлечение данных
        features = data.get("response", {}).get("GeoObjectCollection", {}).get("featureMember", [])
        if not features:
            await message.answer("❌ Адрес не найден. Пример: Москва, Арбат 15")
            return

        first_result = features[0].get("GeoObject", {})
        pos = first_result.get("Point", {}).get("pos", "")
        if not pos:
            await message.answer("❌ Ошибка координат")
            return

        end_lon, end_lat = map(float, pos.split())
        yandex_maps_url = f"https://yandex.ru/maps/?rtext={start_lat},{start_lon}~{end_lat},{end_lon}"
        await message.answer(f"✅ Маршрут: {yandex_maps_url}")

    except requests.exceptions.HTTPError as e:
        logging.error(f"Ошибка API: {e.response.status_code} {e.response.text}")
        await message.answer("⚠️ Проверьте API-ключ Яндекс")
    except json.JSONDecodeError as e:
        logging.error(f"Ошибка JSON: {e}")
        await message.answer("⚠️ Ошибка обработки данных")
    except Exception as e:
        logging.error(f"Ошибка: {str(e)}", exc_info=True)
        await message.answer("⚠️ Системная ошибка")

    await state.clear()

if __name__ == '__main__':
    dp.run_polling(bot)