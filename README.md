# Telegram-бот для построения маршрутов
Бот использует Yandex Geocoder API для поиска адресов.

## Запуск
1. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/Scegocefal/Telegram-bot-geocoder.git
2. Установите зависимости:
   pip install -r requirements.txt
3. **Проверьте `requirements.txt`**  
Убедитесь, что зависимости актуальны:
```txt
aiogram==3.19.0
python-dotenv==1.0.1
requests==2.32.3
4. Создайте файл .env:
   TELEGRAM_TOKEN=ваш_токен
   YANDEX_API_KEY=ваш_ключ
5. Запустите бота:
   python bot.py
