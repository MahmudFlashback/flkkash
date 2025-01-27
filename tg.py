import asyncio
from aiogram import Bot, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
from datetime import datetime, timedelta

TOKEN = '6487033360:AAHXMUMTmZJWtFiT_xOPBwA5URKFQk-0rVo'
bot = Bot(token=TOKEN)

user_states = {}
TIMEOUT = 60  # seconds


async def handle_start(message: types.Message):
    # Просим контакт
    button_phone = KeyboardButton(text="Поделиться номером телефона", request_contact=True)
    markup = ReplyKeyboardMarkup(
        keyboard=[[button_phone]],
        resize_keyboard=True, one_time_keyboard=True
    )
    await message.answer("Добро пожаловать! Пожалуйста, поделитесь вашим номером телефона.", reply_markup=markup)
    user_states[message.from_user.id] = {'state': 'awaiting_contact', 'timestamp': datetime.now()}


async def handle_contact(message: types.Message):
    # Просим геопозицию
    button_location = KeyboardButton(text="Отправить геопозицию", request_location=True)
    markup = ReplyKeyboardMarkup(
        keyboard=[[button_location]],
        resize_keyboard=True, one_time_keyboard=True
    )
    await message.answer("Спасибо! Теперь, пожалуйста, отправьте вашу геопозицию.", reply_markup=markup)
    user_states[message.from_user.id] = {'state': 'awaiting_location', 'timestamp': datetime.now()}


async def handle_location(message: types.Message):
    # Отправляем главное меню
    button_about = KeyboardButton(text="О нас")
    button_contacts = KeyboardButton(text="Контакты")
    button_help = KeyboardButton(text="Помощь")
    button_webapp = KeyboardButton(text="Открыть веб-приложение",
                                   web_app=WebAppInfo(url="https://telegram.org/js/telegram-web-app.js"))

    markup = ReplyKeyboardMarkup(
        keyboard=[[button_about], [button_contacts], [button_help], [button_webapp]],
        resize_keyboard=True, one_time_keyboard=True
    )
    await message.answer("Спасибо! Выберите один из пунктов меню:", reply_markup=markup)
    user_states.pop(message.from_user.id, None)


async def check_timeouts():
    while True:
        for user_id, state_info in list(user_states.items()):
            if datetime.now() - state_info['timestamp'] > timedelta(seconds=TIMEOUT):
                if state_info['state'] == 'awaiting_contact':
                    await bot.send_message(user_id, "Пожалуйста, поделитесь вашим номером телефона.")
                elif state_info['state'] == 'awaiting_location':
                    await bot.send_message(user_id, "Пожалуйста, отправьте вашу геопозицию.")
                user_states[user_id]['timestamp'] = datetime.now()  # Reset timestamp after sending reminder
        await asyncio.sleep(10)


async def main():
    asyncio.create_task(check_timeouts())
    offset = None
    while True:
        updates = await bot.get_updates(offset=offset, timeout=10)
        for update in updates:
            if update.update_id:
                offset = update.update_id + 1
            if update.message:
                message = update.message
                # Обработка текста сообщения
                if message.text:
                    if message.text.startswith('/start'):
                        await handle_start(message)
                    elif message.text == 'О нас':
                        await message.answer("Информация о компании...")
                    elif message.text == 'Контакты':
                        await message.answer("Наши контакты...")
                    elif message.text == 'Помощь':
                        await message.answer("Справочная информация...")
                # Обработка контакта
                elif message.contact:
                    await message.answer(f"Спасибо! Ваш номер телефона: {message.contact.phone_number}")
                    await handle_contact(message)
                # Обработка геопозиции
                elif message.location:
                    await message.answer(
                        f"Спасибо! Ваша геопозиция: широта {message.location.latitude}, долгота {message.location.longitude}")
                    await handle_location(message)
        await asyncio.sleep(1)  # Небольшая задержка


if __name__ == '__main__':
    asyncio.run(main())
