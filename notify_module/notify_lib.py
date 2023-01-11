import sys
import logging
import telebot
import threading
sys.path.append('../')
from sqlite_module.sql_lib import get_all_notifys,create_tables,change_notify_status,midnight_reset_notifications,insert_nofity,get_owner_or_duty_db

#configure logger
notify_logger = logging.getLogger('notify_logger')
notify_logger_formatter = logging.Formatter(
    "%(name)s %(asctime)s %(levelname)s %(message)s")
notify_logger.setLevel(logging.INFO)
notify_logger_logger_handler_file = logging.FileHandler("./logs/notify.log", 'a')
notify_logger_logger_handler_file.setLevel(logging.INFO)
notify_logger_logger_handler_file.setFormatter(notify_logger_formatter)
notify_logger.addHandler(notify_logger_logger_handler_file)


class Notify:
    def __init__(self,id=None,bd_name=None, time=None, work_day=None,text=None, status = 0 , target = "system", active='True'):
        self._id = id
        self._time = time
        self._text = text
        self._work_day = work_day
        self._bd_name = bd_name
        self._target = target
        self._status = status
        self._active = active


class Notifyer(threading.Thread):
    def __init__(self,bot_token:str,*args,**kwargs):
        super().__init__(*args, **kwargs)
        self.notifycations = []
        self.bot_token = bot_token


    def send_notification(self,notify_obj):
        notify_logger.info(f'Отправляем уведомление {notify_obj._bd_name}.')
        try:
            from config import ESS_CHAT_ID
            bot = telebot.TeleBot(self.bot_token)
            duty_engeneer = get_owner_or_duty_db('duty')
            hpsm_owner = get_owner_or_duty_db('owner')
            if notify_obj._target == 'system':
                bot.send_message(ESS_CHAT_ID,notify_obj.format(duty_engeneer=f"[{duty_engeneer['fio']}](tg://user?id={duty_engeneer['tg_id']}",
                hpsm_owner=f"[{hpsm_owner['fio']}](tg://user?id={hpsm_owner['tg_id']}"))
            else:
                bot.send_message(duty_engeneer['tg_id'],notify_obj._text)
            notify_logger.info(f'Уведомление {notify_obj._bd_name}, успешно отправлено.')

        except Exception as exc:
            notify_logger.error(f'Произошла ошибка при отправке уведомления {notify_obj._bd_name}', exc_info=True)


    def check_for_notify(self, obj):
        from datetime import datetime
        current_hour = datetime.now().strftime("%H")
        current_min = datetime.now().strftime("%M")
        notify_hours, notify_min = obj._time.strip().split('-')
        
        current_work_day =  datetime.today().weekday()
        if '-' in obj._work_day:
            notify_start_day, notify_end_day = obj._work_day.split('-')
            notify_work_days = [day for day in range(int(notify_start_day)-1,int(notify_end_day))]
        else:
            notify_work_days = [int(obj._work_day)-1]

        if current_hour == notify_hours and current_min == notify_min and (obj._status == '0' and obj._active=='True') and (current_work_day in notify_work_days):
            notify_logger.info(f'Условия удовлетворяют для срабатывания уведомления {obj._bd_name}')
            #здесь будет проверка на цель для отправки уведомления obj.target = system значит в канал на дежурного и руководителя,
            #user значит только дежурному в личку
            obj._status = '1'
            change_notify_status(obj._bd_name)
            self.send_notification(notify_obj=obj)

        if current_hour == '23' and current_min == '00':
            midnight_reset_notifications()


    def load_all_notyfications_from_db(self):
        notify_logger.info('Загружаем все уведомления из базы данных.')
        try:
            all_notifys = get_all_notifys()
            keys = ("id","bd_name" , "time", "work_day", "text", "target", "status", "active")
            for notify_data in all_notifys:
                self.notifycations.append(Notify(**dict(zip(keys,notify_data))))
            notify_logger.info(f'Загружено {len(self.notifycations)} уведомлений из БД.')
        except Exception as exc:
            notify_logger.error('При загрузке уведомлений произошла ошибка', exc_info=True)

                                                               
    def run(self):
        notify_logger.info('Notifyer запущен.')
        from time import sleep
        self.load_all_notyfications_from_db()
        try:
            while True:
                for _n in self.notifycations:
                    self.check_for_notify(_n)
                sleep(20)
        except Exception as exc:
            notify_logger.error('В процессе работы Notifyer произошла ошибка', exc_info=True)
            
