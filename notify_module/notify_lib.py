import sys
import logging
sys.path.append('../')
from sqlite_module.sql_lib import get_all_notifys,create_tables,change_notify_status,midnight_reset_notifications,insert_nofity

#configure logger
notify_logger = logging.getLogger('notify_logger')
notify_logger_formatter = logging.Formatter(
    "%(name)s %(asctime)s %(levelname)s %(message)s")
notify_logger.setLevel(logging.INFO)
notify_logger_logger_handler_file = logging.FileHandler("notify.log", 'a')
notify_logger_logger_handler_file.setLevel(logging.INFO)
notify_logger_logger_handler_file.setFormatter(notify_logger_formatter)
notify_logger.addHandler(notify_logger_logger_handler_file)


class Notify:
    def __init__(self,bd_name=str, time=str, work_day=str,text=str, status = 0 , target = "system"):
        self._time = time
        self._text = text
        self._work_day = work_day
        self._bd_name = bd_name
        self._target = target
        self._status = status

    def __str__(self):
        return (f'time = {self._time}, bd_name = {self._bd_name}, text = {self._text}')


class Notifyer:
    def __init__(self,path_to_file_with_notifycations= None):
        self.notifycations = []
        self.path_to_file_with_notifycations = path_to_file_with_notifycations

    def check_for_notify(self, obj):
        
        from datetime import datetime
        current_hour = datetime.now().strftime("%H")
        current_min = datetime.now().strftime("%M")
        notify_hours, notify_min = obj._time.strip().split('-')
        
        current_work_day =  datetime.today().weekday()
        notify_start_day, notify_end_day = obj._work_day.split('-')
        
        notify_work_days = [day for day in range(int(notify_start_day)-1,int(notify_end_day))]
        if current_hour == notify_hours and current_min == notify_min and obj._status == '0' and current_work_day in notify_work_days:
            notify_logger.info(f'Условия удовлетворяют для срабатывания уведомления {obj._bd_name}')
            #здесь будет проверка на цель для отправки уведомления obj.target = system значит в канал на дежурного и руководителя,
            #user значит только дежурному в личку
            print(obj)
            obj._status = '1'
            change_notify_status(obj._bd_name)
            print(f'{obj._bd_name} done? {obj._status}')
        else :
            print("Не о чем уведомлять")

    def load_all_notyfications_from_db(self):
        notify_logger.info('Загружаем все уведомления из базы данных.')
        try:
            all_notifys = get_all_notifys()
            keys = ("bd_name" , "time", "work_day", "text", "status", "target")
            for notify_data in all_notifys:
                self.notifycations.append(Notify(**dict(zip(keys,notify_data))))
            print(len(self.notifycations))
        except Exception as exc:
            notify_logger.error('При загрузке уведомлений произошла ошибка', exc_info=True)

    def load_standard_notify_from_file(self):
        from json import load
        try:
            if self.path_to_file_with_notifycations:
                notify_logger.info(f'Загружаем базовые уведомления из файла {self.path_to_file_with_notifycations}')
                with open(self.path_to_file_with_notifycations, 'r', encoding='utf8') as notify_file:
                    data_for_db_insert = load(notify_file)
                    for notify in data_for_db_insert['standard_notify']:
                        insert_nofity(**notify)
                notify_logger.info('Базовые уведомления успешно загружены.')
                return
            notify_logger.info(f'Не задан файл со стандартными уведомлениями, нечего загружать')
        except Exception as exc:
            notify_logger.error('Ошибка загрузки стандартных уведомлений', exc_info=True)
        

    def run(self):
        notify_logger.info('Notifyer запущен.')
        from time import sleep
        self.load_standard_notify_from_file()
        self.load_all_notyfications_from_db()
        try:
            while True:
                for _n in self.notifycations:
                    print(_n._bd_name)
                    self.check_for_notify(_n)
                sleep(20)
        except Exception as exc:
            notify_logger.error('В процессе работы Notifyer произошла ошибка', exc_info=True)
            
