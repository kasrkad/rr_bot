import sqlite3
import time
import logging
import traceback
import time

# logger create
sqlite_logger = logging.getLogger('sqlite_logger')
sqlite_logger_formatter = logging.Formatter(
    "%(name)s %(asctime)s %(levelname)s %(message)s")
sqlite_logger.setLevel(logging.INFO)
sqlite_logger_handler_file = logging.FileHandler("./logs/db_work.log", 'a')
sqlite_logger_handler_file.setLevel(logging.INFO)
sqlite_logger_handler_file.setFormatter(sqlite_logger_formatter)
sqlite_logger_handler_stream = logging.StreamHandler()
sqlite_logger_handler_stream.setLevel(logging.ERROR)
sqlite_logger_handler_stream.setFormatter(sqlite_logger_formatter)

sqlite_logger.addHandler(sqlite_logger_handler_file)
sqlite_logger.addHandler(sqlite_logger_handler_stream)


class SQLite:
    def __init__(self, file='botbase.db'):
        self.file = file

    def __enter__(self):
        self.conn = sqlite3.connect(self.file)
        sqlite_logger.info("Соединение с бд установлено")
        return self.conn.cursor()

    def __exit__(self, type, value, traceback):
        self.conn.commit()
        self.conn.close()
        time.sleep(0.03)
        sqlite_logger.info("Соединение с бд закрыто")


def insert_admin(tg_id=None, fio=None, phone_num=None, duty='NO' ,owner='NO'):
    try:
        sqlite_logger.info(f'Добавляем админа  {tg_id}-{fio}')
        with SQLite() as cursor:
            cursor.execute(
                f"""INSERT INTO ADMIN_USERS(tg_id,fio,phone_num,duty,owner)
                    VALUES ('{tg_id}','{fio}','{phone_num}','{duty}','{owner}')""")
        sqlite_logger.info(f'Администратор {tg_id}-{fio} добавлен.')
    except Exception as exc:
        sqlite_logger.error(
            f'Произошла ошибка при добавлении администратора {tg_id}-{fio}', exc_info=True)


def load_standard_notify_from_file(path_to_file_with_notifycations):
        import json
        try:
            sqlite_logger.info(f'Загружаем базовые уведомления из файла {path_to_file_with_notifycations}')
            if path_to_file_with_notifycations:
                with open(path_to_file_with_notifycations, 'r', encoding='utf8') as notify_file:
                    data_for_db_insert = json.load(notify_file)
                    for notify in data_for_db_insert['standard_notify']:
                        insert_nofity(**notify)
                sqlite_logger.info('Базовые уведомления успешно загружены.')
                return
            sqlite_logger.info(f'Не задан файл со стандартными уведомлениями, нечего загружать')
        except Exception as exc:
            sqlite_logger.error('Ошибка загрузки стандартных уведомлений', exc_info=True)


def load_admin_from_json(path_to_admin_file):
    import json
    sqlite_logger.info(f'Загружаем администраторов из файла {path_to_admin_file}')
    try:
        if path_to_admin_file:
            with open(path_to_admin_file) as json_file:
                json_data = json.load(json_file)
            for admin in json_data['admins']:
                insert_admin(**admin)
            sqlite_logger.info('Администраторы успешно загружены.')
            return
        sqlite_logger.info(f'Не указан файл путь к файлу с администраторами')    
    except Exception as exc:
        sqlite_logger.error(f'Произошла ошибка при загрузке администраторов из {path_to_admin_file}', exc_info=True)


def create_tables() ->None:
    try:
        with SQLite() as cursor:
            cursor.execute(
                """CREATE TABLE IF NOT EXISTS SYSTEM_NOTIFY (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,NOTIFY_NAME TEXT UNIQUE,NOTIFY_TIME TEXT,NOTIFY_WORK_DAY TEXT,NOTIFY_MESSAGE TEXT,NOTIFY_TARGET TEXT default system ,STATUS TEXT default False, ACTIVE TEXT default True)""")
            cursor.execute(
                """CREATE TABLE IF NOT EXISTS ADMIN_USERS (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, tg_id INT NOT NULL UNIQUE, fio TEXT NOT NULL, phone_num TEXT, duty TEXT default NO, owner TEXT default NO)""")
            cursor.execute(
                """CREATE TABLE IF NOT EXISTS HPSM_STATUS (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, task INTEGER, rr_task INTEGER,  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)""")
            cursor.execute("""CREATE TABLE IF NOT EXISTS ARTIFACTS (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, TIMESTAMP DATETIME DEFAULT CURRENT_TIMESTAMP, ARTIFACT_TASK TEXT NOT NULL, STAND TEXT NOT NULL, ACTION TEXT NOT NULL,TASK_COMMIT TEXT, TG_ID INT NOT NULL, COMPLETE TEXT NOT NULL default NO)""")
            cursor.execute(
                """CREATE TABLE IF NOT EXISTS HPSM_STATUS (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, task INTEGER, rr_task INTEGER,  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)""")
            sqlite_logger.info("База данных успешно создана ")
    except Exception as exc:
        print(exc)
        sqlite_logger.error(
            "Произошла ошибка при создании таблиц", exc_info=True)


def insert_nofity(bd_name=str, time=str, work_day=str, text=str, target = "system", active='True') -> None:
    try:
        sqlite_logger.info(f'Добавляем уведомления с именем {bd_name}')
        with SQLite() as cursor:
            cursor.execute(
                f"""INSERT INTO SYSTEM_NOTIFY(NOTIFY_NAME,NOTIFY_TIME,NOTIFY_WORK_DAY,NOTIFY_MESSAGE,NOTIFY_TARGET,ACTIVE)
                    VALUES ('{bd_name}','{time}','{work_day}','{text}','{target}','{active}')""")
        sqlite_logger.info(f'Уведомление {bd_name} добавлено')
    except Exception as exc:
        sqlite_logger.error(
            f'Произошла ошибка при добавлении уведомления {bd_name}', exc_info=True
        )


def set_notify_active(notify_id, active):
    try:
        with SQLite() as cursor:
            sqlite_logger.info(
                f'Изменяем статус уведомления c id = {notify_id} на {active}')
            cursor.execute(f"""UPDATE SYSTEM_NOTIFY SET ACTIVE = '{active}' where id = '{notify_id}';""")
            sqlite_logger.info(
                f'Статус успешно уведомления c id = {notify_id} на {active} успешно изменен.')
        return True
    except Exception as exc:
        sqlite_logger.error(f"Возникла ошибка при запросе уведомлений.",
                            exc_info=True)
        return False


def get_all_notifys():
    try:
        with SQLite() as cursor:
            sqlite_logger.info(
                f'Запрошены все уведомления')
            cursor.execute("""SELECT * FROM SYSTEM_NOTIFY;""")
            sqlite_logger.info(
                f'Уведомления успешно запрошены.')
            return cursor.fetchall()
        return True
    except Exception as exc:
        sqlite_logger.error(f"Возникла ошибка при запросе уведомлений.",
                            exc_info=True)
        return False


def change_notify_status(notify_name):
    try:
        with SQLite() as cursor:
            sqlite_logger.info(
                f'Изменяем статус уведомления {notify_name}')
            cursor.execute(f"""UPDATE SYSTEM_NOTIFY SET STATUS = '1' WHERE NOTIFY_NAME = '{notify_name}';""")
            sqlite_logger.info(
                f'Статус {notify_name} успешно изменен.')
        return True
    except Exception as exc:
        sqlite_logger.error(f"Изменении стауста {notify_name} закончилось ошибкой.",
                            exc_info=True)
        return False


def midnight_reset_notifications():
    try:
        with SQLite() as cursor:
            sqlite_logger.info(
                f'Сбрасываем статусы уведомлений ')
            cursor.execute(f"""UPDATE SYSTEM_NOTIFY SET STATUS = '0';""")
            sqlite_logger.info(
                f'Статусы сброшены.')
        return True
    except Exception as exc:
        sqlite_logger.error(f"Во время сброса статусов произошла ошибка.",
                            exc_info=True)
        return False


def add_admin_user_db(tg_id=None, user_fio=None, user_phone=None) -> bool:
    try:
        with SQLite() as cursor:
            sqlite_logger.info(
                f'Добавляем пользователя id = {tg_id}, fio = {user_fio}, phone = {user_phone}')
            cursor.execute("""INSERT INTO ADMIN_USERS(tg_id,fio,phone_num) VALUES ({tg_id},'{fio}',{phone});""".format(
                tg_id=tg_id, fio=user_fio, phone=user_phone))
            sqlite_logger.info(
                f'Пользователь добавлен id = {tg_id}, fio = {user_fio}, phone = {user_phone}')
        return True
    except sqlite3.IntegrityError as exc:
        sqlite_logger.error(f"Не могу добавить пользователя, значение {exc.args[0].split(':')[1].split('.')[1]} не уникально",
                            exc_info=True)
        return False
    except Exception as exc:
        sqlite_logger.error(
            "Произошла ошибка при добавлении пользователя", exc_info=True)
    return False


def return_phone_num_db(tg_id_for_get_phone):
    try:
        with SQLite() as cursor:
            sqlite_logger.info(f"Запрошен телефон для пользователя {tg_id_for_get_phone}")
            cursor.execute(f"select phone_num from ADMIN_USERS where tg_id = {tg_id_for_get_phone}")
            return cursor.fetchone()[0]
    except Exception as exc:
        sqlite_logger.error(f"Произошла ошибка при запросе телефона для {tg_id_for_get_phone}", exc_info=True)


def show_all_admin_db() -> dict:
    #Нужно будет переделать выбор админа или смотрящего за hpsm на inline keyboard
    try:
        with SQLite() as cursor:
            sqlite_logger.info("Запрошены все доступные администраторы")
            query_result = cursor.execute("Select tg_id,fio from ADMIN_USERS")
            res = { num:f"{tg_id}:{fio}" for num, (tg_id,fio) in enumerate(dict(query_result).items())}
            sqlite_logger.info("Администраторы отданы из бд")
            return res    
    except Exception as exc:
        sqlite_logger.error("Произошла ошибка при запросе администраторов",exc_info=True)


def delete_admin_user_db(admin_id,tg_id_for_delete) -> bool:
    try:
        with SQLite() as cursor:
            sqlite_logger.info(f"Запрошено удаление пользователя {tg_id_for_delete} от администратора {admin_id}")
            cursor.execute(f"DELETE FROM ADMIN_USERS where tg_id = {tg_id_for_delete}")
            sqlite_logger.info(f"Пользователь {tg_id_for_delete} успешно удален")
            return True
    except Exception as exc:
        sqlite_logger.error("Произошла ошибка при удалении администраторов",exc_info=True)


def check_admin_permissions(tg_id_for_check)-> bool:
    try:
        with SQLite() as cursor:
            sqlite_logger.info(f"Проверка пользователя {tg_id_for_check} на наличие прав администратора")
            cursor.execute(f"select * from ADMIN_USERS where tg_id = {tg_id_for_check}")
            if cursor.fetchall():
                return True
            else:
                sqlite_logger.info(f"У пользователя {tg_id_for_check} не найдены права администратора")
                return False
    except Exception as exc:
        sqlite_logger.error(f"При проверке прав доступа пользователя {tg_id_for_check}",exc_info=True)

def set_owner_or_duty_db(tg_id, role='duty'):
    try:
        with SQLite() as cursor:
            sqlite_logger.info(f"Для пользователя {tg_id} устанавливается роль {role}")
            cursor.execute(f"UPDATE ADMIN_USERS SET {role} = 'NO'")
            cursor.execute(f"UPDATE ADMIN_USERS SET {role} = 'YES' where tg_id = {tg_id}")
            sqlite_logger.info(f"Роль {role} для {tg_id} установлена успешно")
    except Exception as exc:
        sqlite_logger.error(f"Произошла ошибка при установке роли-{role} для {tg_id}")


def get_owner_or_duty_db(role='duty')-> dict:
    try:
        with SQLite() as cursor:
            sqlite_logger.info(f"Запрошен текущий {role} из БД")
            query_result = cursor.execute(f"SELECT tg_id, fio from ADMIN_USERS where {role}='YES'").fetchone()
            if query_result:
                return {"tg_id":query_result[0],"fio":query_result[1]}
            return None
    except Exception as exc:
        sqlite_logger.error(f"Произошла ошибка при запросе {role} из БД")


def write_hpsm_status_db(task_count = 0, rr_task_count = 0) -> bool:
    try:
        with SQLite() as cursor:
            if cursor.execute("SELECT * FROM HPSM_STATUS").fetchone():
                cursor.execute(
                    f"UPDATE HPSM_STATUS SET task = {task_count} ,rr_task = {rr_task_count}, timestamp = strftime('%s','now') WHERE id = 1;")
                return True
            cursor.execute(
            f"INSERT INTO HPSM_STATUS (task,rr_task,timestamp) VALUES ({task_count},{rr_task_count},strftime('%s','now'));")
            return True
    except Exception as exc:
        sqlite_logger.error("Произошла ошибка при записи задач HPSM, в таблицу HPSM_STATUS", exc_info=True)
        return False


def get_hpsm_status_db() -> dict:
    try:
        with SQLite() as cursor:
            query_result = cursor.execute("SELECT * FROM HPSM_STATUS").fetchall()
            if query_result:
                return {"tasks": query_result[0], "rr_task":query_result[1], "timestamp": query_result[2]}
            return {"tasks": 0 , "rr_task":0, "timestamp": 0}
    except Exception as exc:
        sqlite_logger.error("Ошибка при получении статуса заявок HPSM")