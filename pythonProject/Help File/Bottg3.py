import os
import sqlite3
from docx import Document
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, CallbackQuery, ReplyKeyboardRemove
from aiogram.utils import executor
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

API_TOKEN = '6843902533:AAHx5B2RunHtix7F9J1QDbIh6Uf_u2uFKi0'
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
name = None
hide_markup = ReplyKeyboardRemove()
class AdminPanelState(StatesGroup):
    MENU = State()
    SHOW_USERS = State()
    ADD_USER = State()
    DELETE_USER = State()
    EXIT_ACCOUNT_CONFIRM = State()

class UserPanelState(StatesGroup):
    MENU = State()
    REPORT = State()
    VIDEO = State()
    EXIT_ACCOUNT_CONFIRM = State()
class Registration(StatesGroup):
    MENU = State()
    INPUT_NAME = State()
    INPUT_PASSWORD = State()

class AuthState(StatesGroup):
    INPUT_NAME = State()
    INPUT_PASSWORD = State()
    CONFIRM_DELETION = State()
    AUTHORIZED = State()
    SHOW_USERS = State()


class MainMenu(StatesGroup):
    MainMenu = State()

@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    await start_message(message)

@dp.message_handler(commands=['version'])
async def version_bot(message: types.Message):
    await message.reply('Версия бота на данный момент 1.2\n'
                        'В данной версии добавлена функция отчета в панель пользователя\n'
                        'Также добавлена функция выхода из аккаунта')


async def start_message(message: types.Message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Регистрация', callback_data='register'))
    markup.add(types.InlineKeyboardButton('Авторизация', callback_data='login'))
    await message.answer('Привет, выбери действие, которое хочешь выполнить', reply_markup=markup)


@dp.callback_query_handler(lambda call: call.data == 'register')
async def handle_register_callback(call: types.CallbackQuery):
    await start_registration(call.message)

# @dp.callback_query_handler(lambda call: call.data == 'login_after_registration')
# async def handle_login_after_registration(call: types.CallbackQuery):
#     await start_login(call.message)

async def start_registration(message: types.Message):
    await message.answer('Введите имя пользователя')
    await Registration.INPUT_NAME.set()


    # @dp.callback_query_handler(lambda call: call.data == 'login')
    # async def handle_login_callback(call: types.CallbackQuery):
    #     await start_login(call.message)
    #
    # async def start_login(message: types.Message):
    #     await message.answer('Введите имя для авторизации')
    #     await AuthState.INPUT_NAME.set()

@dp.message_handler(state=Registration.INPUT_NAME)
async def process_registration_name(message: types.Message, state: FSMContext):
    new_user_name = message.text.strip()

    # Проверка наличия пользователя с таким именем в базе данных
    connection = sqlite3.connect('database.sql')
    cur = connection.cursor()
    cur.execute(f"SELECT * FROM users WHERE name='{new_user_name}'")
    existing_user = cur.fetchone()
    connection.close()

    if existing_user:
        await message.answer(f'Пользователь с именем {new_user_name} уже существует. Введите другое имя.')
        await Registration.INPUT_NAME.set()
    else:
        # Сохранение имени пользователя в контексте
        await state.update_data(new_user_name=new_user_name)

        await message.answer(f'Отлично {new_user_name}. Теперь введите пароль')
        await Registration.INPUT_PASSWORD.set()

@dp.message_handler(state=Registration.INPUT_PASSWORD)
async def process_registration_password(message: types.Message, state: FSMContext):
    password = message.text.strip()

    # Получение имени пользователя из контекста
    data = await state.get_data()
    new_user_name = data.get('new_user_name')

    # Добавление нового пользователя в базу данных
    connection = sqlite3.connect('database.sql')
    cur = connection.cursor()
    cur.execute(f"INSERT INTO users (name, pass) VALUES ('{new_user_name}', '{password}')")
    connection.commit()
    connection.close()

    await message.answer(f'Регистрация успешна! Добро пожаловать, {new_user_name}.')
    # await start_message(message)  # Отправляем обратно в главное меню
    await user_menu(message)  # Переходим к авторизации




# @dp.callback_query_handler(lambda call: call.data == 'login_after_registration')
# async def handle_login_after_registration(call: types.CallbackQuery):
#     await start_login(call.message)

@dp.callback_query_handler(lambda call: call.data == 'login')
async def handle_login_callback(call: types.CallbackQuery):
    await start_login(call.message)


async def start_login(message: types.Message):
    await message.answer('Введите имя для авторизации')
    await AuthState.INPUT_NAME.set()


@dp.message_handler(state=AuthState.INPUT_NAME)
async def check_user_name(message: types.Message, state: FSMContext):
    global name
    name = message.text.strip()

    # Проверка для администратора
    if name == 'NikitaA':
        await message.answer('Введите пароль для администратора')
        await AuthState.INPUT_PASSWORD.set()
    else:
        connection = sqlite3.connect('database.sql')
        cur = connection.cursor()

        cur.execute(f"SELECT * FROM users WHERE name='{name}'")
        user = cur.fetchone()
        connection.close()

        if user:
            await message.answer('Введите пароль для авторизации')
            await AuthState.INPUT_PASSWORD.set()
        else:
            await message.answer('Пользователь с таким именем не найден. Попробуйте ввести имя заново.')

@dp.message_handler(state=AuthState.INPUT_PASSWORD)
async def check_user_password(message: types.Message, state: FSMContext):
    password = message.text.strip()

    # Проверка для администратора
    if name == 'NikitaA' and password == 'ghtpxDf':
        await message.answer(f'Авторизация успешна! Добро пожаловать, администратор {name}')
        await AdminPanelState.MENU.set()  # Переход в состояние админ-меню
        await admin_panel(message, state)
    else:
        connection = sqlite3.connect('database.sql')
        cur = connection.cursor()

        cur.execute(f"SELECT * FROM users WHERE name='{name}' AND pass='{password}'")
        authenticated_user = cur.fetchone()
        connection.close()

        if authenticated_user:
            await message.answer(f'Авторизация успешна! Теперь у вас есть доступ к функционалу.')
            await AuthState.AUTHORIZED.set()
            await user_menu(message)
        else:
            await message.answer('Неверный пароль. Попробуйте ввести пароль заново.')

@dp.message_handler(state=AuthState.AUTHORIZED)
async def authorized_user_functionality(message: types.Message, state: FSMContext):
    await user_menu(message)


async def admin_panel(message: types.Message, state: FSMContext):
    markup = ReplyKeyboardMarkup()
    markup.add(KeyboardButton('Вывести пользователей'))
    markup.add(KeyboardButton('Удалить пользователя'))
    markup.add(KeyboardButton('Выход из аккаунта'))
    await message.answer('Добро пожаловать в меню администратора!', reply_markup=markup)
    await AdminPanelState.MENU.set()

@dp.message_handler(state=AdminPanelState.MENU, text="Выход из аккаунта")
async def admin_exit_account_handler(message: types.Message, state: FSMContext):
    markup = ReplyKeyboardMarkup()
    markup.add(KeyboardButton('Да'))
    markup.add(KeyboardButton('Нет'))
    await message.answer('Вы точно хотите выйти из аккаунта?', reply_markup=markup)
    await AdminPanelState.EXIT_ACCOUNT_CONFIRM.set()

@dp.message_handler(state=AdminPanelState.EXIT_ACCOUNT_CONFIRM, text='Да')
async def admin_exit_account_confirm(message: types.Message, state: FSMContext):
    await start_message(message)
    await state.finish()

@dp.message_handler(state=AdminPanelState.EXIT_ACCOUNT_CONFIRM, text='Нет')
async def process_exit_account_cancel(message: types.Message, state: FSMContext):
    await admin_panel(message, state)
    await AdminPanelState.MENU.set()

@dp.message_handler(text='Вывести пользователей', state=AdminPanelState.MENU)
async def show_users_handler(message: types.Message, state: FSMContext):
    await show_users(message, state)

async def show_users(message: types.Message, state: FSMContext):
    connection = sqlite3.connect('database.sql')
    cur = connection.cursor()
    cur.execute("SELECT * FROM users")
    users = cur.fetchall()
    connection.close()

    if users:
        users_info = "\n".join([f"Имя: {user[1]}, Пароль: {user[2]}" for user in users])
        await message.answer(f'Список пользователей:\n{users_info}')
    else:
        await message.answer('В базе данных нет зарегистрированных пользователей.')
        await AdminPanelState.MENU.set()
#     await AdminPanelState.SHOW_USERS.set()
#
# @dp.message_handler(state=AdminPanelState.SHOW_USERS)
# async def complete_show_users_handler(message: types.Message, state: FSMContext):
#     await message.answer('Действие завершено. Возвращаю в главное меню.')
#     await AdminPanelState.MENU.set()

# @dp.message_handler(text='Добавить пользователя', state=AdminPanelState.MENU)
# async def start_add_user(message: types.Message, state: FSMContext):
#     await message.answer('Введите имя нового пользователя:')
#     await AdminPanelState.ADD_USER.set()
#
# @dp.message_handler(state=AdminPanelState.ADD_USER)
# async def process_add_user_name(message: types.Message, state: FSMContext):
#     new_user_name = message.text.strip()
#
#     # Проверка наличия пользователя с таким именем в базе данных
#     connection = sqlite3.connect('database.sql')
#     cur = connection.cursor()
#     cur.execute(f"SELECT * FROM users WHERE name='{new_user_name}'")
#     existing_user = cur.fetchone()
#     connection.close()
#
#     if existing_user:
#         await message.answer(f'Пользователь с именем {new_user_name} уже существует. Введите другое имя.')
#     else:
#         # Добавление нового пользователя в базу данных
#         cur.execute(f"INSERT INTO users (name, pass) VALUES ('{new_user_name}', 'default_password')")
#         connection.commit()
#         connection.close()
#
#         await message.answer(f'Пользователь {new_user_name} успешно добавлен.')
#
#     # Перевести бота в состояние меню администратора
#     await AdminPanelState.MENU.set()

@dp.message_handler(lambda message: message.text.lower() == 'удалить пользователя', state=AdminPanelState.MENU)
async def start_user_deletion(message: types.Message, state: FSMContext):
    markup = ReplyKeyboardMarkup()
    markup.add(KeyboardButton('Отменить действие'))
    await message.answer('Введите имя пользователя, которого вы хотите удалить:', reply_markup=markup)
    await AdminPanelState.DELETE_USER.set()

@dp.message_handler(text='Отменить действие', state=AdminPanelState.MENU)
async def cancel_action_handler(message: types.Message, state: FSMContext):
    await message.answer('Действие отменено. Возвращаю вас в главное меню администратора.')
    await admin_panel(message, state)


@dp.message_handler(state=AdminPanelState.DELETE_USER)
async def process_user_deletion(message: types.Message, state: FSMContext):
    if message.text.lower() == 'отменить действие':
        await message.answer('Действие отменено. Возвращаю вас в главное меню администратора.')
        await admin_panel(message, state)
        return

    user_name_to_delete = message.text.strip()

    connection = sqlite3.connect('database.sql')
    cur = connection.cursor()
    cur.execute(f"SELECT * FROM users WHERE name='{user_name_to_delete}'")
    existing_user = cur.fetchone()
    connection.close()

    if existing_user:
        await state.update_data(user_to_delete=user_name_to_delete)
        await complete_user_deletion(message, state)
    else:
        await message.answer(f'Пользователь с именем {user_name_to_delete} не найден. Попробуйте ввести имя заново.')

async def complete_user_deletion(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_name_to_delete = data.get('user_to_delete')

    connection = sqlite3.connect('database.sql')
    cur = connection.cursor()
    cur.execute(f"DELETE FROM users WHERE name='{user_name_to_delete}'")
    connection.commit()
    connection.close()

    await message.answer(f'Пользователь {user_name_to_delete} успешно удален.')
    await admin_panel(message, state)

async def user_menu(message: types.Message):
    markup = ReplyKeyboardMarkup()
    markup.add(KeyboardButton('Отчеты'))
    markup.add(KeyboardButton('Видео'))
    markup.add(KeyboardButton('Выход из аккаунта'))
    await message.answer('Добро пожаловать в меню пользователя!', reply_markup=markup)
    await UserPanelState.MENU.set()

@dp.message_handler(state=UserPanelState.MENU, text="Выход из аккаунта")
async def process_exit_account(message: types.Message, state: FSMContext):
    markup = ReplyKeyboardMarkup()
    markup.add(KeyboardButton('Да'))
    markup.add(KeyboardButton('Нет'))
    await message.answer('Вы точно хотите выйти из аккаунта?', reply_markup=markup)
    await UserPanelState.EXIT_ACCOUNT_CONFIRM.set()

@dp.message_handler(state=UserPanelState.EXIT_ACCOUNT_CONFIRM, text='Да')
async def process_exit_account_confirm(message: types.Message, state: FSMContext):
    await start_message(message)
    await state.finish()

@dp.message_handler(state=UserPanelState.EXIT_ACCOUNT_CONFIRM, text='Нет')
async def process_exit_account_cancel(message: types.Message, state: FSMContext):
    await user_menu(message)
    await UserPanelState.MENU.set()




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
    await message.answer("Вы выбрали раздел 'Unity'.")
    await Unity(message, state)

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