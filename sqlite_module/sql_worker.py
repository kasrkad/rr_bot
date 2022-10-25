import sqlite3
import time


class sqlite_worker:

    def __init__(self) -> None:
        self.base_file = 'botbase.db'
        # цепляемся к базе, если ее нет - создаем
        self.connection = sqlite3.connect(
            self.base_file, check_same_thread=False)
        self.cursor = self.connection.cursor()

    def create_tables(self):
        try:
            self.cursor.execute(
                """CREATE TABLE IF NOT EXISTS ADMIN_USERS (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, tg_id INT NOT NULL UNIQUE, fio TEXT NOT NULL, phone_num TEXT, duty TEXT default NO, owner TEXT default NO)""")
            self.cursor.execute(
                """CREATE TABLE IF NOT EXISTS HPSM_STATUS (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, task INTEGER, rr_task INTEGER,  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)""")
            self.cursor.execute("""CREATE TABLE IF NOT EXISTS ARTIFACTS (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, TIMESTAMP DATETIME DEFAULT CURRENT_TIMESTAMP, ARTIFACT_TASK TEXT NOT NULL, STAND TEXT NOT NULL, ACTION TEXT NOT NULL,TASK_COMMIT TEXT, TG_ID INT NOT NULL, COMPLETE TEXT NOT NULL default NO)""")
            self.connection.commit()
        except Exception as exc:
            print(exc)

    def add_admin_user(self, tg_id=None, user_fio=None, user_phone=None) -> None:
        try:
            print(
                f'Добавляем пользователя id = {tg_id}, fio = {user_fio}, phone = {user_phone}')
            self.cursor.execute("""INSERT INTO ADMIN_USERS(tg_id,fio,phone_num) VALUES ({tg_id},'{fio}',{phone});""".format(
                tg_id=tg_id, fio=user_fio, phone=user_phone))
            self.connection.commit()
            return
        except sqlite3.IntegrityError as exc:
            print(
                f"Не могу добавить пользователя, значение {exc.args[0].split(':')[1].split('.')[1]} не уникально")
            return
        except Exception as exc:
            print(exc)
        return

    def return_phone_num(self, tg_id_for_check):
        try:
            self.cursor.execute("""select phone_num from ADMIN_USERS where tg_id = {tg_id}""".format(
                tg_id=tg_id_for_check))
            return self.cursor.fetchone()[0]
        except Exception as exc:
            print(exc)
            return False

    def check_admin_rights(self, tg_id_for_check) -> bool:
        # Проверяем наличие у пользователя админских прав
        try:
            self.cursor.execute(
                """select * from ADMIN_USERS where tg_id = {tg_id}""".format(tg_id=tg_id_for_check))
            if self.cursor.fetchone():
                return True
            return False
        except Exception as exc:
            print(exc)
            return False

    def delete_admin_user(self, tg_id_for_delete) -> bool:
        # Удаление пользователя из администраторов
        try:
            if self.check_admin_rights(tg_id_for_delete):
                self.cursor.execute(
                    "DELETE FROM ADMIN_USERS where tg_id = {tg_id}".format(tg_id=tg_id_for_delete))
                self.connection.commit()
                print('Пользователь удален')
                return True
            else:
                print("Пользователя нет в базе")
                return False
        except Exception as exc:
            print(exc)
            return False

    def set_duty_engeneer(self, tg_id_for_duty) -> dict:
        # Устанавливает нового дежурного, возвращает предыдущего дежурного и нового
        try:
            if self.check_admin_rights(tg_id_for_duty):
                previous_duty_engeneer = self.return_duty_engeneer()
                if previous_duty_engeneer:
                    self.cursor.execute(
                        "UPDATE ADMIN_USERS set duty ='NO' where duty ='YES'")
                    self.connection.commit()
                else:
                    previous_duty_engeneer = None
                self.cursor.execute(
                    "UPDATE ADMIN_USERS SET duty ='YES' WHERE tg_id = {tg_id}".format(tg_id=tg_id_for_duty))
                self.connection.commit()
                next_duty_engeneer = self.return_duty_engeneer()
                return {'prev_eng': previous_duty_engeneer, 'next_eng': next_duty_engeneer}
            print("user not found")
            return False
        except Exception as exc:
            print(exc)
            return False

    def return_duty_engeneer(self) -> dict:
        try:
            self.cursor.execute(
                "select tg_id,fio from ADMIN_USERS where duty = 'YES'")
            duty_tuple = self.cursor.fetchone()
            if duty_tuple:
                return {'tg_id': duty_tuple[0], 'fio': duty_tuple[1]}
            return {"tg_id": "", "fio": "нет дежурного"}
        except Exception as exc:
            print(exc)

    def show_all_admin(self) -> dict:
        try:
            self.cursor.execute("Select tg_id,fio from ADMIN_USERS")
            all_admins = self.cursor.fetchall()
            return dict(all_admins)
        except Exception as exc:
            print(exc)
            return {}

    def set_hpsm_owner(self, owner_tg_id) -> dict:
        if self.return_admin_data_by_tg_id(owner_tg_id):
            prev_owner = self.return_hpsm_owner()  # достаем предыдущего владельца
            # меняем владельца
            self.cursor.execute(
                "update ADMIN_USERS set owner = 'NO' where owner = 'YES'")
            self.cursor.execute(
                "update ADMIN_USERS set owner = 'YES' where tg_id = {tg_id}".format(tg_id=owner_tg_id))
            self.connection.commit()
            new_owner = self.return_hpsm_owner()
            return {'prev_owner': prev_owner, 'new_owner': new_owner}
        else:
            return False


    def return_hpsm_owner(self) -> dict:
        self.cursor.execute(
            "select tg_id,fio from ADMIN_USERS where owner = 'YES'")
        owner = self.cursor.fetchone()
        if owner:
            return {'tg_id': owner[0], 'fio': owner[1]}
        else:
            return {'tg_id': None, 'fio': 'Смотрящий не обнаружен'}

    def return_admin_data_by_tg_id(self, tg_id_for_check):
        self.cursor.execute('select fio from ADMIN_USERS where tg_id = {tg_id}'.format(
            tg_id=tg_id_for_check))
        data = self.cursor.fetchall()
        if data:
            return (tg_id_for_check, data[0][0])
        else:
            return False

    def write_hpsm_status(self, task_count=0, rr_task_count=0) -> None:
        self.connection.commit()
        self.cursor.execute(
            f"INSERT INTO HPSM_STATUS (task,rr_task,timestamp) VALUES ({task_count},{rr_task_count},strftime('%s','now'));")
        self.connection.commit()

    def return_hpsm_status(self) -> dict:
        select = self.cursor.execute(
            """SELECT task,rr_task,timestamp FROM HPSM_STATUS ORDER BY timestamp DESC limit 1""")
        select = select.fetchone()
        return {'tasks': select[0], "rr_tasks": select[1], "timestamp": select[2]}

    def check_rr_count(self) -> int:
        time.sleep(3)
        rr_tasks = self.cursor.execute(
            """SELECT rr_task FROM HPSM_STATUS ORDER BY timestamp DESC limit 1 """)
        rr_tasks = rr_tasks.fetchone()
        return rr_tasks[0]


    def write_cct_load_task(self, simicli_task = None, commit = None, stand = None, action = "load", tg_id = 00000000):
        self.cursor.execute(f"""INSERT INTO ARTIFACTS (TIMESTAMP,ARTIFACT_TASK,STAND,ACTION,TASK_COMMIT,TG_ID,COMPLETE) VALUES (strftime('%s','now'),'{simicli_task}','{stand}','{action}','{commit}',{tg_id},'YES')""")
        self.connection.commit()


    def return_cct_load_history(self):
        data = self.cursor.execute("""SELECT TIMESTAMP,ARTIFACT_TASK,STAND,ACTION,TASK_COMMIT,TG_ID FROM ARTIFACTS""")
        data = self.cursor.fetchall()
        return data