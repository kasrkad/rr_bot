from operator import imod
import telebot
from os import environ
import threading
from ..logger_config.logger_data import create_logger
from ..sqlite_module.sql_lib import get_all_notifys,change_notify_status,midnight_reset_notifications,get_owner_or_duty_db

#configure logger
notify_logger = create_logger(__name__)
ESS_CHAT_ID = environ["ESS_CHAT_ID"]

class Notify:
    """
    Хранит объект уведомления выгружаемый из БД
    """
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
    """_summary_
    Класс уведомителя, получает на вход токен бота через который шлет уведомления
    выгружает данные с БД и создает объекты уведомлений
    Args:
        threading (_type_): _description_
    """
    def __init__(self,bot_token:str,*args,**kwargs):
        super().__init__(*args, **kwargs)
        self.notifycations = []
        self.bot_token = bot_token


    def send_notification(self,notify_obj):
        """Отправка уведомлений из объекта уведомлений

        Args:
            notify_obj (_type_): _description_
        """
        notify_logger.info(f'Отправляем уведомление {notify_obj._bd_name}.')
        try:
            bot = telebot.TeleBot(self.bot_token, parse_mode='MARKDOWN')
            duty_engeneer = get_owner_or_duty_db('duty')
            hpsm_owner = get_owner_or_duty_db('owner')
            if notify_obj._target == 'system':
                bot.send_message(ESS_CHAT_ID,notify_obj._text + f"\n[{duty_engeneer['fio']}](tg://user?id={duty_engeneer['tg_id']}),\n\
[{hpsm_owner['fio']}](tg://user?id={hpsm_owner['tg_id']})")
            else:
                bot.send_message(duty_engeneer['tg_id'],notify_obj._text)
            notify_logger.info(f'Уведомление {notify_obj._bd_name}, успешно отправлено.')

        except Exception as exc:
            notify_logger.error(f'Произошла ошибка при отправке уведомления {notify_obj._bd_name}', exc_info=True)


    def check_for_notify(self, obj):
        """Проверка уведомления на соблюдений условия для отправки

        Args:
            obj (_type_): _description_
        """
        from datetime import datetime
        current_hour = datetime.now().strftime("%H")
        current_min = datetime.now().strftime("%M")
        notify_hours, notify_min = obj._time.strip().split('-')
        current_work_day =  datetime.today().weekday()

        notify_logger.info(f'Проверяю условия day {current_work_day} time {current_hour}-{current_min} для name {obj._bd_name} workdays {obj._work_day} time {obj._time} status {obj._status}')
        
        if '-' in obj._work_day:
            notify_start_day, notify_end_day = obj._work_day.split('-')
            notify_work_days = [day for day in range(int(notify_start_day)-1,int(notify_end_day))]
        else:
            notify_work_days = [int(obj._work_day)-1]
        notify_logger.info(f'Условия для сработки {obj._bd_name} часы {current_hour == notify_hours and current_min == notify_min}, статус и активность {obj._status == "0" and obj._active=="True"}\
            Текущий день входит в день уведомления {current_work_day in notify_work_days}')
        if (current_hour == notify_hours and current_min == notify_min) and (obj._status == '0' and obj._active=='True') and (current_work_day in notify_work_days):
            notify_logger.info(f'Условия удовлетворяют для срабатывания уведомления {obj._bd_name}')
            obj._status = '1'
            change_notify_status(obj._bd_name)
            self.send_notification(notify_obj=obj)

        if current_hour == '23' and current_min == '00':
            """Сбрасываем состояния уведомлений, и перечитывает их из бд"""
            midnight_reset_notifications()
            self.notifycations = []
            self.load_all_notyfications_from_db()


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
            
