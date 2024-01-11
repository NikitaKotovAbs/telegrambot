import os
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

API_TOKEN = '6843902533:AAHx5B2RunHtix7F9J1QDbIh6Uf_u2uFKi0'
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

class UserPanelState(StatesGroup):
    MENU = State()

# Обработчик команды /start
@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    await message.reply("Привет! Отправь мне документ, и я сохраню его в папку 'ReportUnity'.")

# Обработчик документа
@dp.message_handler(content_types=types.ContentType.DOCUMENT)
async def handle_document(message: types.Message):
    # Получаем информацию о документе
    document = message.document
    file_info = await bot.get_file(document.file_id)
    document_file = await bot.download_file(file_info.file_path)

    # Создаем папку 'ReportUnity', если ее нет
    folder_path = 'ReportUnity'
    os.makedirs(folder_path, exist_ok=True)

    # Формируем путь для сохранения документа
    document_path = os.path.join(folder_path, document.file_name)

    # Сохраняем документ
    with open(document_path, 'wb') as file:
        file.write(document_file.read())

    await message.reply(f"Документ '{document.file_name}' сохранен в папке 'ReportUnity'.")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
