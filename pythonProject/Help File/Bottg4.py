import difflib
import os
import aiohttp
import sqlite3
import html
import aiohttp
import asyncio
from html import escape as html_escape
import html2text
from aiogram.types import InlineQuery, InlineQueryResultDocument, InputFile
from docx import Document
from bs4 import BeautifulSoup
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, CallbackQuery, ReplyKeyboardRemove, ParseMode, \
    ContentType, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import executor
import asyncio
import requests
from bs4 import BeautifulSoup as BS
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from datetime import datetime, timedelta

from sqlalchemy.dialects.sqlite import aiosqlite



API_TOKEN = '6843902533:AAHx5B2RunHtix7F9J1QDbIh6Uf_u2uFKi0'
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
name = None
hide_markup = ReplyKeyboardRemove()
url = 'https://mpt.ru/studentu/izmeneniya-v-raspisanii/'
previous_schedule = None
practicals = []
practice_links = {}

class UserPanelState(StatesGroup):
    MENU = State()
    REPORT = State()
    VIDEO = State()
    EXIT_ACCOUNT_CONFIRM = State()


class MainMenu(StatesGroup):
    MainMenu = State()

class AddDocument(StatesGroup):
    enter_practice_name = State()
    wait_document = State()

class UnityReportsState(StatesGroup):
    MAIN_MENU = State()
    PRACTICE_MENU = State()
    ADD_DOCUMENT = State()

class VideoState(StatesGroup):
    MAIN_MENU = State()
    PRACTICE_MENU = State()
    ADD_DOCUMENT = State()
    ADD_PRACTICE = State()
    ADD_LINK = State()








async def check_schedule():
    global previous_schedule

    while True:
        response = requests.get(url)
        soup = BS(response.content, 'html.parser')

        replacement_blocks = soup.select('.table-responsive table.table-striped')

        current_schedule = []

        for block in replacement_blocks:
            group_info = block.select_one('caption b')
            group_name = group_info.text if group_info else "Информация о группе не найдена"

            if "П50-2-22" in group_name:
                group_schedule = []
                for row in block.select('tr')[1:]:
                    lesson_number = row.select_one('.lesson-number').text
                    replace_from = row.select_one('.replace-from').text
                    replace_to = row.select_one('.replace-to').text
                    updated_at_str = row.select_one('.updated-at').text

                    lesson_info = {
                        'lesson_number': lesson_number,
                        'replace_from': replace_from,
                        'replace_to': replace_to,
                        'updated_at': updated_at_str
                    }

                    group_schedule.append(lesson_info)

                current_schedule.append({'group_name': group_name, 'schedule': group_schedule})

        if previous_schedule != current_schedule:
            previous_schedule = current_schedule
            await send_schedule_changes(current_schedule)

        await asyncio.sleep(10)


async def send_schedule_changes(schedule):
    for group_schedule in schedule:
        group_name = group_schedule['group_name']
        group_schedule_info = group_schedule['schedule']

        message_text = f"Изменения в расписании для группы {group_name}:\n"

        for lesson_info in group_schedule_info:
            message_text += (
                f"Пара: {lesson_info['lesson_number']}\n"
                f"Что заменяют: {lesson_info['replace_from']}\n"
                f"На что заменяют: {lesson_info['replace_to']}\n"
                f"Замена добавлена: {lesson_info['updated_at']}\n\n"
            )

        # Отправка сообщения о изменениях в чат бота
        await bot.send_message(chat_id='1388135173', text=message_text)

@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    await message.reply('Версия бота на данный момент 1.3 LITE')
    await user_menu(message)

# @dp.message_handler(commands=['linkdatabase'])
# async def linkdatabase_command(message: types.Message):
#     await fetch_data_from_linkdatabase(message.chat.id)
#     await UserPanelState.MENU.set()
#     await user_menu(message)








async def user_menu(message: types.Message):
    markup = ReplyKeyboardMarkup()
    markup.add(KeyboardButton('Расписание экзаменов (NEW)'))
    markup.add(KeyboardButton('Отчеты'))
    markup.add(KeyboardButton('Видео'))
    await message.answer('Выберите опцию:', reply_markup=markup)
    await UserPanelState.MENU.set()

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
    # Ваш код обработки отчетов
    # Например, вызов функции для отправки отчетов
    await reports(message)

async def reports(message: types.Message):
    markup = ReplyKeyboardMarkup()
    markup.add(KeyboardButton('Unity отчёты'))
    markup.add(KeyboardButton('ТУТ'))
    markup.add(KeyboardButton('ТАМ'))
    markup.add(KeyboardButton('Назад'))
    await message.answer('Добро пожаловать в меню пользователя!', reply_markup=markup)

@dp.message_handler(state=UserPanelState.MENU, text="Unity отчёты")
async def process_unity_reports(message: types.Message, state: FSMContext):
    await message.answer("Вы выбрали раздел 'Unity отчёты'.")
    await unity_reports_menu(message, state)  # Добавлен state

async def unity_reports_menu(message: types.Message, state: FSMContext):
    markup = ReplyKeyboardMarkup()
    markup.add(KeyboardButton('Практическая №1'))
    markup.add(KeyboardButton('Практическая №2'))
    markup.add(KeyboardButton('Практическая №3'))
    for practical in practicals:
        markup.add(KeyboardButton(practical))
    markup.add(KeyboardButton('Добавить новую практическую с документом'))
    markup.add(KeyboardButton('Назад'))
    await message.answer('Выберите опцию:', reply_markup=markup)
    await UnityReportsState.MAIN_MENU.set()

@dp.message_handler(state=UserPanelState.MENU, text="Добавить новую практическую с документом")
async def add_practice_with_document_transfer(message: types.Message, state: FSMContext):
    await add_practice_with_document(message, state)

async def add_practice_with_document(message: types.Message, state: FSMContext):
    await message.answer("Введите название новой практической:")
    await AddDocument.enter_practice_name.set()


@dp.message_handler(state=AddDocument.enter_practice_name)
async def handle_practice_name(message: types.Message, state: FSMContext):
    # Сохраняем название практической в состояние
    async with state.proxy() as data:
        data['new_practice_name'] = message.text

    # Запрашиваем у пользователя документ
    await message.answer("Теперь отправьте документ для практической:")
    await AddDocument.wait_document.set()

@dp.message_handler(state=AddDocument.wait_document, content_types=types.ContentType.DOCUMENT)
async def handle_document_for_practice(message: types.Message, state: FSMContext):
    # Получаем информацию о документе
    document = message.document
    file_info = await bot.get_file(document.file_id)
    document_file = await bot.download_file(file_info.file_path)

    # Получаем название практической из состояния
    async with state.proxy() as data:
        practice_name = data['new_practice_name']

    # Создаем папку 'ReportUnity', если ее нет
    folder_path = 'ReportUnity'
    os.makedirs(folder_path, exist_ok=True)

    # Формируем путь для сохранения документа
    document_path = os.path.join(folder_path, document.file_name)

    # Сохраняем документ
    with open(document_path, 'wb') as file:
        file.write(document_file.read())

    # Добавляем новую практическую в список
    practicals.append(practice_name)
    # Сохраняем ссылку на файл для данной практической
    practice_links[practice_name] = document_path

    # Создаем кнопку для новой практической
    markup = InlineKeyboardMarkup()
    # Вместо использования callback_data, используем switch_inline_query_current_chat
    markup.add(InlineKeyboardButton(f'Практическая: {practice_name}', switch_inline_query_current_chat=f'show_practice_{practice_name}'))

    # Возвращаемся в главное меню
    await user_menu(message)
    await UserPanelState.MENU.set()

    # Отправляем сообщение с кнопкой
    await message.answer(f"Новая практическая '{practice_name}' добавлена!", reply_markup=markup)


@dp.inline_handler(lambda query: query.query.startswith('show_practice_'))
async def show_practice_file(inline_query: InlineQuery):
    # Получаем название практической из query
    practice_name = inline_query.query[len('show_practice_'):]

    # Получаем путь к файлу
    file_path = practice_links.get(practice_name)

    if file_path:
        # Отправляем файл пользователю
        with open(file_path, 'rb') as file:
            await bot.send_document(inline_query.from_user.id, InputFile(file))

    else:
        await bot.send_message(inline_query.from_user.id, f"Для практической '{practice_name}' нет сохраненного файла.")





@dp.message_handler(state=UserPanelState.MENU, text="Видео")
async def process_video(message: types.Message, state: FSMContext):
    await message.answer("Вы выбрали раздел 'Видео'.")
    await video(message)


async def video(message: types.Message):
    markup = ReplyKeyboardMarkup()
    markup.add(KeyboardButton('Unity Video'))
    markup.add(KeyboardButton('LinkDataBase'))
    markup.add(KeyboardButton('Назад'))
    await message.answer('Добро пожаловать в меню пользователя!', reply_markup=markup)


@dp.message_handler(state=UserPanelState.MENU, text="Unity Video")
async def process_video(message: types.Message, state: FSMContext):
    await message.answer("Вы выбрали раздел 'Видео'.")
    await Unity_video(message, state)


@dp.message_handler(state=UserPanelState.MENU, text="LinkDataBase")
async def process_linkdatabase(message: types.Message, state: FSMContext):
    await message.answer("Вы выбрали раздел 'LinkDataBase'.")
    # Передаем chat_id в функцию fetch_data_from_linkdatabase
    await fetch_data_from_linkdatabase(message.chat.id)


async def fetch_data_from_linkdatabase(chat_id):
    conn = sqlite3.connect('linkdatabase.sql')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM linkdatabase')
    rows = cursor.fetchall()

    for row in rows:
        message_text = f"ID: {row[0]}, User ID: {row[1]}, Practice Name: {row[2]}, Link: {row[3]}"
        await bot.send_message(chat_id, message_text)

    # Закрытие соединения с базой данных
    conn.close()


async def Unity_video(message: types.Message, state: FSMContext):
    markup = ReplyKeyboardMarkup()
    markup.add(KeyboardButton('Практическая №1'))
    markup.add(KeyboardButton('Практическая №2'))
    for practical in practicals:
        markup.add(KeyboardButton(practical))
    markup.add(KeyboardButton('Добавить видео для практической'))
    markup.add(KeyboardButton('Назад'))
    await message.answer('Добро пожаловать в меню пользователя!', reply_markup=markup)
    await VideoState.MAIN_MENU.set()


@dp.message_handler(state=UserPanelState.MENU, text="Добавить видео для практической")
async def add_practice(message: types.Message, state: FSMContext):
    await message.answer("Введите название новой практической:")
    # Помечаем, что пользователь сейчас добавляет новую практическую
    async with state.proxy() as data:
        data['new_practice'] = True
    # Переключаем состояние в ожидание ответа с новым названием практической
    await VideoState.ADD_PRACTICE.set()


@dp.message_handler(state=VideoState.ADD_PRACTICE)
async def handle_new_practice(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if data.get('new_practice'):
            # Добавляем новую практическую в список
            new_practice = message.text
            practicals.append(new_practice)
            # Спрашиваем у пользователя ввести ссылку на файл
            await message.answer(f"Введите ссылку на файл для практической '{new_practice}':")
            # Переключаем состояние в ожидание ответа с новой ссылкой
            await VideoState.ADD_LINK.set()


@dp.message_handler(state=VideoState.ADD_LINK)
async def handle_practice_link(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        # Получаем последнюю добавленную практическую
        new_practice = practicals[-1]
        # Сохраняем ссылку на файл для данной практической
        practice_links[new_practice] = message.text

        # Сохраняем ссылку в базе данных
        conn = sqlite3.connect('linkdatabase.sql')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO linkdatabase (user_id, practice_name, link)
            VALUES (?, ?, ?)
        ''', (message.from_user.id, new_practice, message.text))
        conn.commit()
        conn.close()

        data['new_practice'] = False
        # Возвращаемся в главное меню
        await Unity_video(message, state)
        # Сбрасываем состояние
        await UserPanelState.MENU.set()

@dp.message_handler(state=UserPanelState.MENU, text="Назад")
async def go_back(message: types.Message, state: FSMContext):
    await user_menu(message)
    await UserPanelState.MENU.set()

@dp.message_handler(state=UserPanelState.MENU, text="Добавить практическую")
async def add_practice(message: types.Message, state: FSMContext):
    await message.answer("Введите название новой практической:")
    # Помечаем, что пользователь сейчас добавляет новую практическую
    async with state.proxy() as data:
        data['new_practice'] = True
    # Переключаем состояние в ожидание ответа с новым названием практической
    await UserPanelState.ADD_PRACTICE.set()

@dp.message_handler(state=UserPanelState.MENU)
async def handle_menu(message: types.Message, state: FSMContext):
    if message.text in practicals:
        # Если сообщение совпадает с одной из практических, отправляем сохраненную ссылку
        practice_name = message.text
        link = practice_links.get(practice_name)
        if link:
            await message.answer(f"Ссылка для практической '{practice_name}': {link}")
        else:
            await message.answer(f"Для практической '{practice_name}' нет сохраненной ссылки.")
    elif message.text.lower() == "назад":  # Убедимся, что текст нормализован (в нижний регистр)
        await Unity_video(message, state)
        await UserPanelState.MENU.set()
    else:
        await message.answer("Выберите опцию из меню.")







loop = asyncio.get_event_loop()
loop.create_task(check_schedule())
executor.start_polling(dp, skip_updates=True)
