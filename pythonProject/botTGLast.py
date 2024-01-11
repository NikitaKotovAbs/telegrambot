import difflib
import os
import aiohttp
import sqlite3
import html
import aiohttp
import asyncio
import gspread
from html import escape as html_escape
from google.auth.transport.requests import Request
import io
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import gdown
from pathlib import Path
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
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from sqlalchemy.dialects.sqlite import aiosqlite



API_TOKEN = '6843902533:AAHx5B2RunHtix7F9J1QDbIh6Uf_u2uFKi0'
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
name = None
hide_markup = ReplyKeyboardRemove()
url = 'https://mpt.ru/studentu/izmeneniya-v-raspisanii/'
previous_schedule = None
# Инициализация PyDrive
gauth = GoogleAuth()
gauth.LocalWebserverAuth()  # Создайте файл settings.yaml для хранения учетных данных

drive = GoogleDrive(gauth)
class UserPanelState(StatesGroup):
    MENU = State()
    REPORT = State()
    VIDEO = State()


class MainMenu(StatesGroup):
    MainMenu = State()


class UnityReportsState(StatesGroup):
    MAIN_MENU = State()
    PRACTICE_MENU = State()
    ADD_DOCUMENT = State()
    WAITING_FOR_DOCUMENT_NAME = State()


class VideoState(StatesGroup):
    MAIN_MENU = State()
    ADD_VIDEO_NAME = State()
    ADD_VIDEO_LINK = State()
    VIEW_VIDEO_LINK = State()
    WAITING_FOR_VIDEO_NAME = State()

class VideoState_TRZBD(StatesGroup):
    MAIN_MENU = State()
    ADD_VIDEO_NAME = State()
    ADD_VIDEO_LINK = State()
    VIEW_VIDEO_LINK = State()
    WAITING_FOR_VIDEO_NAME = State()

class DocumentState(StatesGroup):
    MAIN_MENU = State()
    PRACTICE_MENU = State()
    ADD_DOCUMENT = State()
    WAITING_FOR_DOCUMENT_NAME_ADD = State()
    WAITING_FOR_DOCUMENT_NAME_VIEW = State()

class ReportState(StatesGroup):
    MAIN_MENU = State()

class YouTubeState(StatesGroup):
    MAIN_MENU_Y = State()
    LINK_YOUTUBE = State()
    DATA_YOUTUBE = State()





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

            if "П50-5-21" in group_name:
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

        await asyncio.sleep(1800)


async def send_schedule_changes(schedule):
    for group_schedule in schedule:
        group_name = group_schedule['group_name']
        group_schedule_info = group_schedule['schedule']

        message_text = f"<b>Изменения в расписании для группы {group_name}:</b>\n\n"

        for lesson_info in group_schedule_info:
            message_text += (
                f"Пара: {lesson_info['lesson_number']}\n"
                f"<b>Что заменяют:</b> <u>{lesson_info['replace_from']}\n</u>"
                f"<b>На что заменяют:</b> <u>{lesson_info['replace_to']}\n\n</u>"
                f"Замена добавлена: {lesson_info['updated_at']}\n\n"

            )

        # Отправка сообщения о изменениях в чат бота с использованием HTML
        await bot.send_message(chat_id='1388135173', text=message_text, parse_mode="HTML")

@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    await message.reply('Версия бота на данный момент 1.1 Beta')
    await user_menu(message)

# @dp.message_handler(commands=['linkdatabase'])
# async def linkdatabase_command(message: types.Message):
#     await fetch_data_from_linkdatabase(message.chat.id)
#     await UserPanelState.MENU.set()
#     await user_menu(message)








async def user_menu(message: types.Message):
    markup = ReplyKeyboardMarkup()
    markup.add(KeyboardButton('Отчеты'))
    markup.add(KeyboardButton('Видео'))
    markup.add(KeyboardButton('Журнал посещаемости'))
    markup.add(KeyboardButton('Расписание занятий'))
    markup.add(KeyboardButton('Расписание УП'))

    await message.answer('Выберите опцию:', reply_markup=markup)
    await UserPanelState.MENU.set()




@dp.message_handler(state=UserPanelState.MENU, text="Журнал посещаемости")
async def process_journal(message: types.Message, state: FSMContext):
    await message.answer("Информация о посещаемости")

    spreadsheet_url = 'https://docs.google.com/spreadsheets/d/1Zc2W09sz9m6o-KNb2umPZo7UlrDyHOSuT_xaBvGcUM0/edit#gid=0'
    current_directory = os.path.dirname(os.path.realpath(__file__))

    # Постройте относительный путь к файлу JSON
    json_path = os.path.join(current_directory, 'storagetelegramfile-3619dea7a060.json')

    # Используйте относительный путь для инициализации службы Google Sheets
    gc = gspread.service_account(filename=json_path)
    worksheet = gc.open_by_url(spreadsheet_url).sheet1
    cell_data = worksheet.get_all_values()

    # Форматирование данных для вывода в чат
    formatted_data = format_table(cell_data)

    # Отправьте данные в чат бота
    await message.answer(formatted_data)

    await message.answer("\nСсылка на таблицу: https://docs.google.com/spreadsheets/d/1K4nUwbj1jwpuBZV_9BiDut0ybn-oUqsrHwFQ6wrQRuA/edit#gid=0 ")
    await user_menu(message)


def format_table(cell_data):
    # Формируем строку с заголовками
    headers = cell_data[0]
    formatted_table = f"{headers[0]}\t{headers[1]}\t{headers[2]}\t{headers[3]}\n"

    # Проходим по строкам данных
    for row in cell_data[1:]:
        # Извлекаем нужные данные из каждой строки
        name = row[0]
        respectful_absences = row[1]
        disrespectful_absences = row[2]
        all_absences = row[3]

        # Формируем строку с данными
        formatted_row = f"{name}\t\t\t\t\t\t\t\t\t\t{respectful_absences}\t\t{disrespectful_absences}\t\t\t{all_absences}\n"
        formatted_table += formatted_row

    return formatted_table

@dp.message_handler(state=UserPanelState.MENU, text="Расписание УП")
async def process_journal(message: types.Message, state: FSMContext):
    text = "Расписание УП"
    await message.answer("Вы выбрали раздел 'Расписание УП'.")
    await send_image(message, state, text)

@dp.message_handler(state=UserPanelState.MENU, text="Расписание занятий")
async def process_reports(message: types.Message, state: FSMContext):
    await message.answer("Вы выбрали раздел 'Расписание занятий'.")
    text = "Расписание занятий"
    await send_image(message, state, text)

# Обработка нажатия на кнопку "Отправить картинку"

async def send_image(message: types.Message, state: FSMContext, text: str):
    # Получите текущую директорию вашего проекта
    current_directory = os.path.dirname(os.path.realpath(__file__))
    if text == "Расписание занятий":
        # Постройте относительный путь к файлу Exam.jpg
        relative_path = os.path.join(current_directory, 'ExamSchedule', 'schedule.jpeg')

        # Используйте относительный путь
        doc_path = relative_path

        # Отправляем документ пользователю
        with open(doc_path, "rb") as doc_file:
            await message.answer_document(doc_file, caption=f"Расписание занятий")
    else:
        # Постройте относительный путь к файлу Exam.jpg
        relative_path = os.path.join(current_directory, 'ExamSchedule', 'YP.jpeg')

        # Используйте относительный путь
        doc_path = relative_path

        # Отправляем документ пользователю
        with open(doc_path, "rb") as doc_file:
            await message.answer_document(doc_file, caption=f"Расписание занятий")
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
    markup.add(KeyboardButton('ТРЗБД отчёты'))
    markup.add(KeyboardButton('Arduino отчёты'))
    markup.add(KeyboardButton('ТРПО отчёты'))
    markup.add(KeyboardButton('ИСР.ПО отчёты'))
    markup.add(KeyboardButton('РМП отчёты'))
    markup.add(KeyboardButton('Назад'))
    await message.answer('Добро пожаловать в меню пользователя!', reply_markup=markup)
    await ReportState.MAIN_MENU.set()

@dp.message_handler(state=ReportState.MAIN_MENU, text="Unity отчёты")
async def process_unity_reports(message: types.Message, state: FSMContext):
    await message.answer("Вы выбрали раздел 'Unity отчёты'.")
    await unity_reports_menu(message, state, folder_id='1N9RjYdJHjZ_Xwv4HGD7ePXV9ZQv7OMi0')  # Добавлен state

@dp.message_handler(state=ReportState.MAIN_MENU, text="ТРЗБД отчёты")
async def process_unity_reports(message: types.Message, state: FSMContext):
    await message.answer("Вы выбрали раздел 'ТРЗБД отчёты'.")
    await unity_reports_menu(message, state, folder_id='1Jqgeot4hVzM6eACxe3fAVvhorhfHdzhE')  # Добавлен state

@dp.message_handler(state=ReportState.MAIN_MENU, text="Arduino отчёты")
async def process_unity_reports(message: types.Message, state: FSMContext):
    await message.answer("Вы выбрали раздел 'Arduino отчёты'.")
    await unity_reports_menu(message, state, folder_id='1d8qcXYSJvwpx74RFkmdPdAT3vR_qsKrC')  # Добавлен state

@dp.message_handler(state=ReportState.MAIN_MENU, text="ТРПО отчёты")
async def process_unity_reports(message: types.Message, state: FSMContext):
    await message.answer("Вы выбрали раздел 'ТРПО отчёты'.")
    await unity_reports_menu(message, state, folder_id='1bPVVu0RAkKnCxsUJqOpOzwI9TDEuTqof')  # Добавлен state

@dp.message_handler(state=ReportState.MAIN_MENU, text="ИСР.ПО отчёты")
async def process_unity_reports(message: types.Message, state: FSMContext):
    await message.answer("Вы выбрали раздел 'ИСР.ПО отчёты'.")
    await unity_reports_menu(message, state, folder_id='1dFn-DPHv2-f4WHeBqp-4azGvqU-yiOUX')  # Добавлен state

@dp.message_handler(state=ReportState.MAIN_MENU, text="РМП отчёты")
async def process_unity_reports(message: types.Message, state: FSMContext):
    await message.answer("Вы выбрали раздел 'РМП отчёты'.")
    await unity_reports_menu(message, state, folder_id='18YJIzP4pgYSAFtQB5NuyBb-YDNZXLPeY')  # Добавлен state

async def unity_reports_menu(message: types.Message, state: FSMContext, folder_id: str):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(KeyboardButton('Вывод документов'))
    markup.add(KeyboardButton('Добавить документ'))
    markup.add(KeyboardButton('Все документы'))
    markup.add(KeyboardButton('Назад'))
    await message.answer('Выберите опцию:', reply_markup=markup)
    await DocumentState.MAIN_MENU.set()
    await state.update_data(folder_id=folder_id)
    # await UnityReportsState.MAIN_MENU.set()

@dp.message_handler(state=DocumentState.MAIN_MENU, text="Все документы")
async def request_full_document(message: types.Message, state: FSMContext):
    data = await state.get_data()
    folder_id = data.get('folder_id')
    documents = get_documents_from_google_drive("", folder_id)  # Передаем пустую строку вместо document_name

    if documents:
        # Если есть документы, формируем текстовое сообщение
        document_names = "\n".join(doc['title'] for doc in documents)
        response_text = f"Список всех документов:\n{document_names}"
    else:
        # Если нет документов, формируем соответствующее сообщение
        response_text = "В данной папке нет документов."

    await message.answer(response_text)


# Обработчик команды "Сами документы"
@dp.message_handler(state=DocumentState.MAIN_MENU, text="Вывод документов")
async def request_document_name(message: Message, state: FSMContext):
    # Запрашиваем название файла
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Отменить действие', callback_data='cancel_action'))
    await message.answer("Введите название документа:", reply_markup=markup)
    await DocumentState.WAITING_FOR_DOCUMENT_NAME_VIEW.set()

# Обработчик ввода названия файла
@dp.message_handler(state=DocumentState.WAITING_FOR_DOCUMENT_NAME_VIEW)
async def process_document_name(message: Message, state: FSMContext):
    document_name = message.text
    data = await state.get_data()
    folder_id = data.get('folder_id')
    # Получаем список документов из Google Drive
    documents = get_documents_from_google_drive(document_name, folder_id)

    if documents:
        for document in documents:
            document_id = document['id']
            document_title = document['title']

            # Скачиваем файл
            document_file = drive.CreateFile({'id': document_id})
            document_file.GetContentFile(document_title)

            # Отправляем документ пользователю
            with open(document_title, 'rb') as document_file:
                await message.answer_document(document_file, caption=f"Документ: {document_title}")

            # Удаляем локальную копию файла
            os.remove(document_title)


        await user_menu(message)
        await UserPanelState.MENU.set()
    else:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('Отменить действие', callback_data='cancel_action'))
        await message.reply("Документ с указанным названием не найден. Попробуйте снова.", reply_markup=markup)


# @dp.message_handler(state=DocumentState.MAIN_MENU, text="Сами документы")
# async def send_documents(message: types.Message):
#     # Выводим список документов из Google Drive
#     documents = get_documents_from_google_drive()
#
#     if documents:
#         for document in documents:
#             document_id = document['id']
#             document_title = document['title']
#             document_file = drive.CreateFile({'id': document_id})
#             document_file.GetContentFile(document_title)  # Скачиваем файл
#
#             with open(document_title, 'rb') as document_file:
#                 await message.answer_document(document_file, caption=f"Документ: {document_title}")
#
#             os.remove(document_title)  # Удаляем локальную копию файла
#
#     else:
#         await message.reply("В папке нет сохраненных документов.")
#
#     await user_menu(message)
#     await UserPanelState.MENU.set()
#
def get_documents_from_google_drive(document_name, folder_id):
    gauth = GoogleAuth()
    gauth.LocalWebserverAuth()

    drive = GoogleDrive(gauth)

    # folder_id = '1N9RjYdJHjZ_Xwv4HGD7ePXV9ZQv7OMi0'

    file_list = drive.ListFile({'q': f"'{folder_id}' in parents and trashed=false"}).GetList()

    documents = []
    for file in file_list:
        if file['mimeType'] == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
            # Добавляем только те документы, название которых содержит искомую строку
            if document_name.lower() in file['title'].lower():
                documents.append({'id': file['id'], 'title': file['title']})

    return documents



@dp.message_handler(state=DocumentState.MAIN_MENU, text="Добавить документ")
async def add_document_start(message: types.Message, state: FSMContext):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Отменить действие', callback_data='cancel_action'))
    await message.answer("Названия файлов должны иметь такой вид:\n" "Практическая работа №(1,2.3...)\n\n"
                         "Иначе будут модерироваться")
    await message.answer("Введите название практической:", reply_markup=markup)
    await DocumentState.WAITING_FOR_DOCUMENT_NAME_ADD.set()


@dp.message_handler(state=DocumentState.WAITING_FOR_DOCUMENT_NAME_ADD)
async def add_document_name(message: types.Message, state: FSMContext):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Отменить действие', callback_data='cancel_action'))
    document_name = message.text

    if await check_existing_file(document_name, state):
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('Отменить действие', callback_data='cancel_action'))
        document_name = message.text
        await message.answer(

            f"Файл с именем '{document_name}' уже существует на Google Диске. Пожалуйста, введите другое имя.", reply_markup=markup)
        return

    await state.update_data(document_name=document_name)
    await message.answer(f"Отлично! Теперь отправьте документ для практической '{document_name}'.", reply_markup=markup)
    await DocumentState.ADD_DOCUMENT.set()

async def check_existing_file(document_name, state):
    data = await state.get_data()
    folder_id = data.get('folder_id')

    # Инициализация PyDrive
    gauth = GoogleAuth()
    gauth.LocalWebserverAuth()  # Создайте файл settings.yaml для хранения учетных данных
    drive = GoogleDrive(gauth)

    # Проверяем наличие файла с таким именем в папке на Google Диске
    file_list = drive.ListFile({'q': f"'{folder_id}' in parents and title = '{document_name}.docx'"}).GetList()
    return len(file_list) > 0

# Измененный код сохранения документа
@dp.message_handler(content_types=types.ContentType.DOCUMENT, state=DocumentState.ADD_DOCUMENT)
async def add_document(message: types.Message, state: FSMContext):
    # Получаем данные из состояния
    data = await state.get_data()
    document_name = data.get("document_name")

    data = await state.get_data()
    folder_id = data.get('folder_id')

    # Сохраняем документ в папку на Google Drive
    await save_to_google_drive(message.document.file_id, document_name, folder_id)

    await message.answer(f"Документ для практической '{document_name}' успешно добавлен и сохранен на Google Drive!")
    await DocumentState.MAIN_MENU.set()
    await user_menu(message)



async def save_to_google_drive(file_id, document_name, folder_id, is_docx=True):
    try:
        # Получаем информацию о файле из Telegram
        file_info = await bot.get_file(file_id)
        file_path = file_info.file_path
        file_url = f"https://api.telegram.org/file/bot{API_TOKEN}/{file_path}"

        # Скачиваем файл
        async with aiohttp.ClientSession() as session:
            async with session.get(file_url) as response:
                content = await response.read()

        # Определяем расширение файла
        file_extension = '.pdf' if not is_docx else '.docx'

        # Создаем файл документа
        # doc_path = f"C:\\BotTG\\pythonProject\\ExamSchedule\\{document_name}{file_extension}"
        current_directory = os.path.dirname(os.path.realpath(__file__))
        # Постройте относительный путь с использованием переменных
        doc_path = os.path.join(current_directory, 'ExamSchedule', f"{document_name}{file_extension}")
        with open(doc_path, "wb") as doc_file:
            doc_file.write(content)

        # Если файл .docx, то сохраняем его в папку на Google Drive
        if is_docx:
            # Инициализация PyDrive
            gauth = GoogleAuth()
            gauth.LocalWebserverAuth()  # Создайте файл settings.yaml для хранения учетных данных
            drive = GoogleDrive(gauth)

            # Получаем ID папки на Google Drive
            # folder_id = '1N9RjYdJHjZ_Xwv4HGD7ePXV9ZQv7OMi0'

            # Загружаем файл .docx в папку на Google Drive
            file_drive = drive.CreateFile({'title': f"{document_name}.docx", 'parents': [{'id': folder_id}]})
            file_drive.SetContentFile(doc_path)
            file_drive.Upload()

            print(f"Файл '{document_name}.docx' успешно сохранен на Google Drive!")
        else:
            print(f"Файл '{document_name}.pdf' успешно сохранен на локальном диске.")

    except Exception as e:
        print(f"Ошибка при сохранении файла: {e}")



@dp.message_handler(state=UserPanelState.MENU, text="Видео")
async def process_video(message: types.Message, state: FSMContext):
    await message.answer("Вы выбрали раздел 'Видео'.")
    await video(message)


async def video(message: types.Message):
    markup = ReplyKeyboardMarkup()
    markup.add(KeyboardButton('Unity Video'))
    markup.add(KeyboardButton('ТРЗБД Video'))
    markup.add(KeyboardButton('YouTube для залива'))
    markup.add(KeyboardButton('Назад'))
    await message.answer('Добро пожаловать в меню пользователя!', reply_markup=markup)


@dp.message_handler(state=UserPanelState.MENU, text="Unity Video")
async def process_video(message: types.Message, state: FSMContext):
    await message.answer("Вы выбрали раздел 'Видео'.")
    await Unity_video(message, state)

@dp.message_handler(state=UserPanelState.MENU, text="ТРЗБД Video")
async def process_video(message: types.Message, state: FSMContext):
    await message.answer("Вы выбрали раздел 'Видео'.")
    await TRZBD_video(message, state)

@dp.message_handler(state=UserPanelState.MENU, text="YouTube для залива")
async def process_video(message: types.Message, state: FSMContext):
    await YouTube(message, state)

async def YouTube(message: types.Message, state: FSMContext):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(KeyboardButton('Ссылка на YouTube'))
    markup.add(KeyboardButton('Данные от аккаунта'))
    markup.add(KeyboardButton('Назад'))
    await message.answer('Вы выбрали раздел "YouTube для залива"', reply_markup=markup)
    await YouTubeState.MAIN_MENU_Y.set()

@dp.message_handler(state=YouTubeState.MAIN_MENU_Y, text="Ссылка на YouTube")
async def process_video(message: types.Message, state: FSMContext):
    await message.answer("Ссылка на YouTube канал для загрузки видео:"
                         "'https://www.youtube.com/channel/UCVdRL6XK6tz9UIR_dLP80XQ'")
    await YouTube(message, state)

@dp.message_handler(state=YouTubeState.MAIN_MENU_Y, text="Данные от аккаунта")
async def request_password(message: types.Message, state: FSMContext):
    await message.answer("Введите пароль для доступа к данным:")
    # Устанавливаем состояние ожидания пароля
    await YouTubeState.DATA_YOUTUBE.set()

@dp.message_handler(state=YouTubeState.DATA_YOUTUBE)
async def process_password(message: types.Message, state: FSMContext):
    # Получаем введенный пароль из сообщения
    entered_password = message.text
    password = "Ghty2s"

    # Предположим, что у вас есть функция check_password, которая проверяет пароль
    if entered_password == password:
        # Пароль верный, переключаемся на метод вывода данных
        await message.answer("Пароль верный. Ваши данные:"
                             "\n Логин: mptvideost@gmail.com"
                             "\n Пароль: GhrbfT2dbF")
        await process_video(message, state)
    else:
        # Пароль неверный, возвращаем пользователя в меню
        await message.answer("Неверный пароль")
        await YouTube(message, state)


async def Unity_video(message: types.Message, state: FSMContext):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(KeyboardButton('Вывод видео'))
    markup.add(KeyboardButton('Добавить видео для практической'))
    markup.add(KeyboardButton('Вывести все видео'))
    markup.add(KeyboardButton('Назад'))
    await message.answer('Добро пожаловать в меню пользователя!', reply_markup=markup)
    await VideoState.MAIN_MENU.set()

async def TRZBD_video(message: types.Message, state: FSMContext):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(KeyboardButton('Вывод видео'))
    markup.add(KeyboardButton('Добавить видео для практической'))
    markup.add(KeyboardButton('Вывести все видео'))
    markup.add(KeyboardButton('Назад'))
    await message.answer('Добро пожаловать в меню пользователя!', reply_markup=markup)
    await VideoState_TRZBD.MAIN_MENU.set()

@dp.message_handler(state=VideoState.MAIN_MENU, text="Вывести все видео")
async def process_linkdatabase(message: types.Message, state: FSMContext):
    await message.answer("Вы выбрали раздел 'Все видео'.")
    # Передаем chat_id в функцию fetch_data_from_linkdatabase
    await fetch_data_from_linkdatabase_unity(message.chat.id)

@dp.message_handler(state=VideoState_TRZBD.MAIN_MENU, text="Вывести все видео")
async def process_linkdatabase(message: types.Message, state: FSMContext):
    await message.answer("Вы выбрали раздел 'Все видео'.")
    # Передаем chat_id в функцию fetch_data_from_linkdatabase
    await fetch_data_from_linkdatabase_trzbd(message.chat.id)

async def fetch_data_from_linkdatabase_unity(chat_id):
    # Подключение к базе данных
    conn = sqlite3.connect('videodatabase.sql')
    cursor = conn.cursor()
    # Выполнение SQL-запроса
    cursor.execute('SELECT * FROM videodatabase')
    rows = cursor.fetchall()
    # Закрытие соединения с базой данных
    conn.close()
    # Собираем все данные в одну строку
    if not rows:
        # Если нет строк, то отправляем сообщение о том, что ссылок нет
        await bot.send_message(chat_id, "Ссылок в базе данных нет.")
    else:
        # Собираем все данные в одну строку
        message_text = "\n".join([f"Наименование: {row[1]}\nСсылка: {row[2]}\n" for row in rows])
        # Отправка сообщения с данными из базы данных
        await bot.send_message(chat_id, message_text)

async def fetch_data_from_linkdatabase_trzbd(chat_id):
    # Подключение к базе данных
    conn = sqlite3.connect('videodatabasetrzbd.sql')
    cursor = conn.cursor()
    # Выполнение SQL-запроса
    cursor.execute('SELECT * FROM videodatabase')
    rows = cursor.fetchall()
    # Закрытие соединения с базой данных
    conn.close()
    # Собираем все данные в одну строку
    if not rows:
        # Если нет строк, то отправляем сообщение о том, что ссылок нет
        await bot.send_message(chat_id, "Ссылок в базе данных нет.")
    else:
        # Собираем все данные в одну строку
        message_text = "\n".join([f"Наименование: {row[1]}\nСсылка: {row[2]}\n" for row in rows])
        # Отправка сообщения с данными из базы данных
        await bot.send_message(chat_id, message_text)



@dp.message_handler(state=VideoState.MAIN_MENU, text="Вывод видео")
async def ask_video_name(message: types.Message, state: FSMContext):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Отменить действие', callback_data='cancel_action'))
    await message.answer("Введите название видео:", reply_markup=markup)
    await VideoState.WAITING_FOR_VIDEO_NAME.set()

@dp.message_handler(state=VideoState_TRZBD.MAIN_MENU, text="Вывод видео")
async def ask_video_name(message: types.Message, state: FSMContext):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Отменить действие', callback_data='cancel_action'))
    await message.answer("Введите название видео:", reply_markup=markup)
    await VideoState_TRZBD.WAITING_FOR_VIDEO_NAME.set()

@dp.message_handler(state=VideoState.WAITING_FOR_VIDEO_NAME)
async def view_single_video(message: types.Message, state: FSMContext):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Отменить действие', callback_data='cancel_action'))
    video_name = message.text

    # Выводим сохраненное видео из базы данных по указанному названию
    video = fetch_video_by_name_unity(video_name)
    if video:
        video_text = f"*{video['practice_name']}*, [\\{video['video_link']}]({video['video_link']})"
        await message.reply(f"Найденное видео:\n{video_text}", parse_mode=types.ParseMode.MARKDOWN)
        await user_menu(message)
    else:
        await message.reply(f"Видео с названием '{video_name}' не найдено. Попробуйте ввести название еще раз.", reply_markup=markup)
        await VideoState.WAITING_FOR_VIDEO_NAME.set()

def fetch_video_by_name_unity(video_name):
    # Получение данных из базы данных по названию видео
    conn = sqlite3.connect('videodatabase.sql')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM videodatabase WHERE practice_name=?', (video_name,))
    row = cursor.fetchone()
    conn.close()

    # Преобразование данных в словарь
    if row:
        video = {'practice_name': row[1], 'video_link': row[2]}
        return video
    else:
        return None

@dp.message_handler(state=VideoState_TRZBD.WAITING_FOR_VIDEO_NAME)
async def view_single_video(message: types.Message, state: FSMContext):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Отменить действие', callback_data='cancel_action'))
    video_name = message.text

    # Выводим сохраненное видео из базы данных по указанному названию
    video = fetch_video_by_name_trzbd(video_name)
    if video:
        video_text = f"*{video['practice_name']}*, [\\{video['video_link']}]({video['video_link']})"
        await message.reply(f"Найденное видео:\n{video_text}", parse_mode=types.ParseMode.MARKDOWN)
        await user_menu(message)
    else:
        await message.reply(f"Видео с названием '{video_name}' не найдено. Попробуйте ввести название еще раз.", reply_markup=markup)
        await VideoState_TRZBD.WAITING_FOR_VIDEO_NAME.set()

def fetch_video_by_name_trzbd(video_name):
    # Получение данных из базы данных по названию видео
    conn = sqlite3.connect('videodatabasetrzbd.sql')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM videodatabase WHERE practice_name=?', (video_name,))
    row = cursor.fetchone()
    conn.close()

    # Преобразование данных в словарь
    if row:
        video = {'practice_name': row[1], 'video_link': row[2]}
        return video
    else:
        return None



@dp.message_handler(state=VideoState.MAIN_MENU, text="Добавить видео для практической")
async def add_video(message: types.Message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Отменить действие', callback_data='cancel_action'))
    await message.answer("Названия файлов должны иметь такой вид:\n" "Практическая работа №(1,2.3...)\n\n"
                         "Иначе будут модерироваться")
    await message.answer("Введите название практической работы:", reply_markup=markup)
    await VideoState.ADD_VIDEO_NAME.set()

@dp.message_handler(state=VideoState_TRZBD.MAIN_MENU, text="Добавить видео для практической")
async def add_video(message: types.Message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Отменить действие', callback_data='cancel_action'))
    await message.answer("Название видео должны иметь такой вид:\n" "Практическая работа №(1,2.3...)\n\n"
                         "Иначе будут модерироваться")
    await message.answer("Введите название видео:", reply_markup=markup)
    await VideoState_TRZBD.ADD_VIDEO_NAME.set()


@dp.message_handler(state=VideoState.ADD_VIDEO_NAME)
async def process_video_data(message: types.Message, state: FSMContext):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Отменить действие', callback_data='cancel_action'))
    practice_name = message.text

    # Сохранение введенного названия практической работы в состояние FSMContext
    await state.update_data(practice_name=practice_name)

    await message.answer("Введите ссылку на видео:", reply_markup=markup)
    await VideoState.ADD_VIDEO_LINK.set()

@dp.message_handler(state=VideoState_TRZBD.ADD_VIDEO_NAME)
async def process_video_data(message: types.Message, state: FSMContext):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Отменить действие', callback_data='cancel_action'))
    practice_name = message.text

    # Сохранение введенного названия практической работы в состояние FSMContext
    await state.update_data(practice_name=practice_name)

    await message.answer("Введите ссылку на видео:", reply_markup=markup)
    await VideoState_TRZBD.ADD_VIDEO_LINK.set()



@dp.message_handler(state=VideoState.ADD_VIDEO_LINK)
async def process_video_link(message: types.Message, state: FSMContext):
    # Получение данных из состояния FSMContext
    data = await state.get_data()
    practice_name = data.get('practice_name')
    video_link = message.text

    # Сохранение в базе данных
    conn = sqlite3.connect('videodatabase.sql')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO videodatabase (practice_name, video_link) VALUES (?, ?)',
                   (practice_name, video_link))
    conn.commit()
    conn.close()

    await message.answer("Видео успешно добавлено!")

    # Сброс состояния, чтобы вернуться в главное меню
    await user_menu(message)
    await UserPanelState.MENU.set()

@dp.message_handler(state=VideoState_TRZBD.ADD_VIDEO_LINK)
async def process_video_link(message: types.Message, state: FSMContext):
    # Получение данных из состояния FSMContext
    data = await state.get_data()
    practice_name = data.get('practice_name')
    video_link = message.text

    # Сохранение в базе данных
    conn = sqlite3.connect('videodatabasetrzbd.sql')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO videodatabase (practice_name, video_link) VALUES (?, ?)',
                   (practice_name, video_link))
    conn.commit()
    conn.close()

    await message.answer("Видео успешно добавлено!")

    # Сброс состояния, чтобы вернуться в главное меню
    await user_menu(message)
    await UserPanelState.MENU.set()



@dp.message_handler(state=[ReportState.MAIN_MENU, UserPanelState.MENU, YouTubeState.MAIN_MENU_Y], text="Назад")
async def go_back(message: types.Message, state: FSMContext):
    await user_menu(message)
    await UserPanelState.MENU.set()

@dp.message_handler(state=DocumentState.MAIN_MENU, text="Назад")
async def go_back(message: types.Message, state: FSMContext):
    await reports(message)
    await ReportState.MAIN_MENU.set()
#
# @dp.message_handler(state=DocumentState.MAIN_MENU, text="Назад")
# async def go_back(message: types.Message, state: FSMContext):
#     await user_menu(message)
#     await UserPanelState.MENU.set()

@dp.callback_query_handler(lambda c: c.data == 'cancel_action', state=[DocumentState.WAITING_FOR_DOCUMENT_NAME_ADD, DocumentState.WAITING_FOR_DOCUMENT_NAME_VIEW, VideoState.ADD_VIDEO_NAME, VideoState.WAITING_FOR_VIDEO_NAME, DocumentState.ADD_DOCUMENT, VideoState.ADD_VIDEO_LINK, VideoState.WAITING_FOR_VIDEO_NAME, VideoState.MAIN_MENU])
async def cancel_action(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.answer("Действие отменено.")
    await DocumentState.MAIN_MENU.set()
    await user_menu(callback_query.message)




loop = asyncio.get_event_loop()
loop.create_task(check_schedule())
executor.start_polling(dp, skip_updates=True)
