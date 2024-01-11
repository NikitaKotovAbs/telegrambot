import sqlite3

# conn = sqlite3.connect('linkdatabase.sql')
# cursor = conn.cursor()
#
# cursor.execute('''
#     CREATE TABLE IF NOT EXISTS linkdatabase (
#         id INTEGER PRIMARY KEY AUTOINCREMENT,
#         user_id INTEGER,
#         practice_name TEXT,
#         link TEXT
#     )
# ''')
#
# conn.commit()
# conn.close()
import sqlite3
# Инициализация базы данных для видео
conn_video = sqlite3.connect('videodatabasetrzbd.sql')
cursor_video = conn_video.cursor()
cursor_video.execute('CREATE TABLE IF NOT EXISTS videodatabase (id INTEGER PRIMARY KEY AUTOINCREMENT, '
                     'practice_name TEXT, video_link TEXT)')
conn_video.commit()
conn_video.close()


# def fetch_data_from_linkdatabase():
#
#         # Подключение к базе данных
#         conn = sqlite3.connect('worddatabase.sql')
#         cursor = conn.cursor()
#
#         # Выполнение запроса для выборки данных
#         cursor.execute('SELECT * FROM linkdatabase')
#
#         # Извлечение всех строк из результата
#         rows = cursor.fetchall()
#
#         # Вывод данных
#         for row in rows:
#             print(f"ID: {row[0]}, User ID: {row[1]}, Practice Name: {row[2]}, Link: {row[3]}")
#
#         # Закрытие соединения с базой данных
#         conn.close()


# Вызываем функцию для вывода данных
# fetch_data_from_linkdatabase()

# import sqlite3
#
# def create_documents_table():
#     # Подключаемся к базе данных
#     conn = sqlite3.connect('word_database.sql')
#     cursor = conn.cursor()
#
#     # Создаем таблицу documents
#     cursor.execute('''
#         CREATE TABLE IF NOT EXISTS documents (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             user_id INTEGER NOT NULL,
#             practice_name TEXT NOT NULL,
#             file_path TEXT NOT NULL,
#             FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE ON UPDATE CASCADE
#         )
#     ''')
#
#     # Сохраняем изменения и закрываем соединение
#     conn.commit()
#     conn.close()
#
# # Вызываем функцию для создания таблицы documents
# create_documents_table()

# import sqlite3
#
# def update_documents_table():
#     # Подключаемся к базе данных
#     conn = sqlite3.connect('word_database.sql')
#     cursor = conn.cursor()
#
#     # Добавляем столбец user_id, если его еще нет
#     cursor.execute('PRAGMA foreign_keys=off;')
#
#     # Создаем временную таблицу documents_backup
#     cursor.execute('''
#         CREATE TABLE IF NOT EXISTS documents_backup (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             practice_name TEXT NOT NULL,
#             file_path TEXT NOT NULL
#         )
#     ''')
#
#     # Копируем данные из documents в documents_backup
#     cursor.execute('INSERT INTO documents_backup SELECT id, practice_name, file_path FROM documents')
#
#     # Удаляем старую таблицу documents
#     cursor.execute('DROP TABLE IF EXISTS documents')
#
#     # Создаем новую таблицу documents с добавлением столбца user_id
#     cursor.execute('''
#         CREATE TABLE IF NOT EXISTS documents (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             user_id INTEGER NOT NULL,
#             practice_name TEXT NOT NULL,
#             file_path TEXT NOT NULL,
#             FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE ON UPDATE CASCADE
#         )
#     ''')
#
#     # Восстанавливаем данные из documents_backup в новую таблицу documents
#     cursor.execute('INSERT INTO documents SELECT id, 0, practice_name, file_path FROM documents_backup')
#
#     # Удаляем временную таблицу documents_backup
#     cursor.execute('DROP TABLE IF EXISTS documents_backup')
#
#     # Сохраняем изменения и закрываем соединение
#     conn.commit()
#     conn.close()
#
# # Вызываем функцию для обновления структуры таблицы
# update_documents_table()