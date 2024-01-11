import difflib
import os
import aiohttp
import sqlite3
import html
import aiohttp
import asyncio
from html import escape as html_escape
import html2text
from docx import Document
from bs4 import BeautifulSoup
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, CallbackQuery, ReplyKeyboardRemove, ParseMode
from aiogram.utils import executor
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import executor
WEB_PAGE_URL = 'https://mpt.ru/studentu/izmeneniya-v-raspisanii/'
CHAT_ID = '1388135173'
API_TOKEN = '6843902533:AAHx5B2RunHtix7F9J1QDbIh6Uf_u2uFKi0'
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
name = None
hide_markup = ReplyKeyboardRemove()
h = html2text.HTML2Text()
h.ignore_links = True
h.ignore_images = True

class UserPanelState(StatesGroup):
    MENU = State()
    REPORT = State()
    VIDEO = State()
    EXIT_ACCOUNT_CONFIRM = State()



class MainMenu(StatesGroup):
    MainMenu = State()

@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    await message.reply('Версия бота на данный момент 1.1 LITE')
    await user_menu(message)


# @dp.message_handler(commands=['version'])
# async def version_bot(message: types.Message):
#     await message.reply('Версия бота на данный момент 1.2\n'
#                         'В данной версии добавлена функция отчета в панель пользователя\n'
#                         'Также добавлена функция выхода из аккаунта')


async def user_menu(message: types.Message):
    markup = ReplyKeyboardMarkup()
    markup.add(KeyboardButton('Расписание экзаменов (NEW)'))
    markup.add(KeyboardButton('Отчеты'))
    markup.add(KeyboardButton('Видео'))
    await message.answer('Выберите опцию:', reply_markup=markup)
    await UserPanelState.MENU.set()





# @dp.callback_query_handler(lambda call: call.data == 'register')
# async def handle_register_callback(call: types.CallbackQuery):
#     await start_registration(call.message)

@dp.message_handler(state=UserPanelState.MENU, text="Расписание экзаменов (NEW)")
async def process_reports(message: types.Message, state: FSMContext):
    await message.answer("Вы выбрали раздел 'Расписание экзаменов (NEW)'.")
    await send_image(message, state)

# Обработка нажатия на кнопку "Отправить картинку"

async def send_image(message: types.Message, state: FSMContext):
    # Путь к файлу
    doc_path = "C:\\BotTG\\pythonProject\\ExamSchedule\\Exam.jpg"

    # Отправляем документ пользователю
    with open(doc_path, "rb") as doc_file:
        await message.answer_document(doc_file, caption=f"Расписание экзаменов (NEW)")

    # Сброс состояния, чтобы остаться в текущем меню
    await user_menu(message)

@dp.message_handler(state=UserPanelState.MENU, text="Отчеты")
async def process_reports(message: types.Message, state: FSMContext):
    await message.answer("Вы выбрали раздел 'Отчеты'.")
    await report(message)

@dp.message_handler(state=UserPanelState.MENU, text="Видео")
async def process_video(message: types.Message, state: FSMContext):
    await message.answer("Вы выбрали раздел 'Видео'.")
    await video(message)

async def video(message: types.Message):
    markup = ReplyKeyboardMarkup()
    markup.add(KeyboardButton('Unity Video'))
    markup.add(KeyboardButton('Назад'))
    await message.answer('Добро пожаловать в меню пользователя!', reply_markup=markup)

@dp.message_handler(state=UserPanelState.MENU, text="Unity Video")
async def process_reports(message: types.Message, state: FSMContext):
    await message.answer("Вы выбрали раздел 'Видео'.")
    await Unity_video(message, state)

async def Unity_video(message: types.Message, state: FSMContext):
    markup = ReplyKeyboardMarkup()
    markup.add(KeyboardButton('Практическая №1'))
    markup.add(KeyboardButton('Практическая №2'))
    markup.add(KeyboardButton('Практическая №3'))
    markup.add(KeyboardButton('Назад'))
    await message.answer('Добро пожаловать в меню пользователя!', reply_markup=markup)
async def report(message: types.Message):
    markup = ReplyKeyboardMarkup()
    markup.add(KeyboardButton('Unity'))
    markup.add(KeyboardButton('РМП'))
    markup.add(KeyboardButton('СП'))
    markup.add(KeyboardButton('Назад'))
    await message.answer('Добро пожаловать в меню пользователя!', reply_markup=markup)


@dp.message_handler(state=UserPanelState.MENU, text="Unity")
async def process_reports(message: types.Message, state: FSMContext):
    await message.answer("Вы выбрали разделе отчётов 'Unity'.")
    await Unity_number_reports(message, state)

async def Unity_number_reports(message: types.Message, state: FSMContext):
    markup = ReplyKeyboardMarkup()
    markup.add(KeyboardButton('Практическая №1'))
    markup.add(KeyboardButton('Практическая №2'))
    markup.add(KeyboardButton('Практическая №3'))
    markup.add(KeyboardButton('Практическая №4'))
    markup.add(KeyboardButton('Практическая №5'))
    markup.add(KeyboardButton('Практическая №6'))
    markup.add(KeyboardButton('Практическая №7'))
    markup.add(KeyboardButton('Практическая №8'))
    markup.add(KeyboardButton('Назад'))
    await message.answer('Добро пожаловать в меню пользователя!', reply_markup=markup)


# @dp.message_handler(state=UserPanelState.MENU, text="Unity")
# async def process_reports(message: types.Message, state: FSMContext):
#     await message.answer("Вы выбрали раздел 'Unity'.")
#     await Unity(message, state)

@dp.message_handler(state=UserPanelState.MENU, text="РМП")
async def process_reports(message: types.Message, state: FSMContext):
    await message.answer("Вы выбрали раздел 'РМП'.")
    await RMP(message, state)

@dp.message_handler(state=UserPanelState.MENU, text="СП")
async def process_reports(message: types.Message, state: FSMContext):
    await message.answer("Вы выбрали раздел 'СП'.")
    await SP(message, state)

@dp.message_handler(state=UserPanelState.MENU, text="Назад")
async def process_reports(message: types.Message):
    await message.answer("Возвращаю вас в меню пользователя'.")
    await user_menu(message)

async def Unity(message: types.Message, state: FSMContext):
    # Путь к файлу
    doc_path = "C:\\BotTG\\pythonProject\\ReportUnity\\UnityReport.docx"

    # Отправляем документ пользователю
    with open(doc_path, "rb") as doc_file:
        await message.answer_document(doc_file, caption=f"Отчет по Unity: UnityReport.docx")

    # Сброс состояния, чтобы остаться в текущем меню
    await UserPanelState.MENU.set()


async def RMP(message: types.Message, state: FSMContext):
    # Путь к файлу
    doc_path = "C:\\BotTG\\pythonProject\\ReportUnity\\UnityReport.docx"

    # Отправляем документ пользователю
    with open(doc_path, "rb") as doc_file:
        await message.answer_document(doc_file, caption=f"Отчет по Unity: UnityReport.docx")

    # Сброс состояния, чтобы остаться в текущем меню
    await UserPanelState.MENU.set()


async def SP(message: types.Message, state: FSMContext):
    # Путь к файлу
    doc_path = "C:\\BotTG\\pythonProject\\ReportUnity\\UnityReport.docx"

    # Отправляем документ пользователю
    with open(doc_path, "rb") as doc_file:
        await message.answer_document(doc_file, caption=f"Отчет по Unity: UnityReport.docx")

    # Сброс состояния, чтобы остаться в текущем меню
    await UserPanelState.MENU.set()

    # Сброс состояния, что

# async def video(message: types.Message):
#     markup = ReplyKeyboardMarkup()
#     markup.add(KeyboardButton('Отчеты'))
#     markup.add(KeyboardButton('Видео'))
#     await message.answer('Добро пожаловать в меню пользователя!', reply_markup=markup)
#     await AuthState.AUTHORIZED.set()
# if __name__ == '__main__':
executor.start_polling(dp, skip_updates=True)