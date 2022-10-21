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

sqlite_logger_handler_file = logging.FileHandler("db_work.log", 'a')
sqlite_logger_handler_file.setLevel(logging.INFO)
sqlite_logger_handler_file.setFormatter(sqlite_logger_formatter)

sqlite_logger_handler_stream = logging.StreamHandler()
sqlite_logger_handler_stream.setLevel(logging.ERROR)
sqlite_logger_handler_stream.setFormatter(sqlite_logger_formatter)

sqlite_logger.addHandler(sqlite_logger_handler_file)
sqlite_logger.addHandler(sqlite_logger_handler_stream)


class SQLite():
    def __init__(self, file='botbase.db'):
        self.file = file

    def __enter__(self):
        self.conn = sqlite3.connect(self.file)
        # self.conn.row_factory = sqlite3.Row
        sqlite_logger.info("Соединение с бд установлено")
        return self.conn.cursor()

    def __exit__(self, type, value, traceback):
        self.conn.commit()
        self.conn.close()
        time.sleep(0.03)
        sqlite_logger.info("Соединение с бд закрыто")



def create_tables() ->None:
    try:
        with SQLite() as cursor:
            cursor.execute(
                """CREATE TABLE IF NOT EXISTS ADMIN_USERS (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, tg_id INT NOT NULL UNIQUE, fio TEXT NOT NULL, phone_num TEXT, duty TEXT default NO, owner TEXT default NO)""")
            cursor.execute(
                """CREATE TABLE IF NOT EXISTS HPSM_STATUS (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, task INTEGER, rr_task INTEGER,  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)""")
            cursor.execute("""CREATE TABLE IF NOT EXISTS ARTIFACTS (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, TIMESTAMP DATETIME DEFAULT CURRENT_TIMESTAMP, ARTIFACT_TASK TEXT NOT NULL, STAND TEXT NOT NULL, ACTION TEXT NOT NULL,TASK_COMMIT TEXT, TG_ID INT NOT NULL, COMPLETE TEXT NOT NULL default NO)""")
            sqlite_logger.info("База данных успешно создана ")

    except Exception as exc:
        print(exc)
        sqlite_logger.error(
            "Произошла ошибка при создании таблиц", exc_info=True)


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
            cursor.execute("select phone_num from ADMIN_USERS where tg_id = {tg_id}")
            return cursor.fetchall()[0]
    except Exception as exc:
        sqlite_logger.error(f"Произошла ошибка при запросе телефона для {tg_id_for_get_phone}", exc_info=True)
        
        
def show_all_admin_db() -> dict:
    #Нужно будет переделать выбор админа или смотрящего за hpsm на inline keyboard
    try:
        with SQLite() as cursor:
            sqlite_logger.info("Запрошены все доступные администраторы")
            cursor.execute("Select tg_id,fio from ADMIN_USERS")
            sql_query_result = cursor.fetchall()
            res = { num:f"{tg_id}:{fio}" for num, (tg_id,fio) in enumerate(dict(sql_query_result).items())}
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


def set_owner_or_duty(tg_id, role=duty):
    try:
        with SQLite() as cursor:
            sqlite_logger.info(f"Для пользователя {tg_id} устанавливается роль {role}")
            cursor.execute(f"UPDATE ADMIN_USERS SET {role} = 'NO'")
            cursor.execute(f"UPDATE ADMIN_USERS SET {role} = 'YES' where tg_id = {tg_id}")
            sqlite_logger.info(f"Роль {role} для {tg_id} установлена успешно")
    except Exception as exc:
        sqlite_logger.error(f"Произошла ошибка при установке роли-{role} для {tg_id}")


def get_owner_or_duty(tg_id, role=duty)-> dict:
    try:
        with SQLite() as cursor:
            sqlite_logger.info(f"Запрошен текущий {role} из БД")
            cursor.execute(f"SELECT tg_id, fio from ADMIN_USERS where {role}='YES'")
            query_result = cursor.fetchone()
            if query_result:
                return {"tg_id":query_result[0],"fio":query_result[1]}
            return None
    except Exception as exc:
        sqlite_logger.error(f"Произошла ошибка при запросе {role} из БД")


def permissions_decorator(func_for_decorate):
    
    def wrapper(message):
        if check_admin_permissions(message.from_user.id):
            func_for_decorate(message)
        else:
            raise ValueError("В доступе отказано")
    return wrapper




def main():
    print(check_admin_permissions(2848131471))

if __name__ == "__main__":
    main()
