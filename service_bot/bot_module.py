import sys
sys.path.append('../')
import logging
import telebot
from sqlite_module import sql_lib
from asterisk_module import asterisk_lib
from config import *
import os

#configure logger
service_bot_logger = logging.getLogger('service_bot_logger')
service_bot_logger_formatter = logging.Formatter(
    "%(name)s %(asctime)s %(levelname)s %(message)s")
service_bot_logger.setLevel(logging.INFO)
service_bot_logger_logger_handler_file = logging.FileHandler("service_bot_logger.log", 'a')
service_bot_logger_logger_handler_file.setLevel(logging.INFO)
service_bot_logger_logger_handler_file.setFormatter(service_bot_logger_formatter)
service_bot_logger.addHandler(service_bot_logger_logger_handler_file)

class Ess_service_bot:

    
    def __init__(self, bot_token):
        self.bot = telebot.TeleBot(bot_token, parse_mode='MARKDOWN')
        self.document_regexp = r"[a-z0-9]{8}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{12}"

    
    def permissions_decorator(self,func_for_decorate):
        def wrapper(message):
            print(message)
            if sql_lib.check_admin_permissions(message.from_user.id):
                func_for_decorate(message)
            else:
                raise ValueError("В доступе отказано")
        return wrapper

    def initilize(self,path_to_admin_json, path_to_notify_json):
        try:
            service_bot_logger.info('Инициализируем бота, загружаем админов и уведомления.')
            if not os.path.exists('botbase.db'):
                sql_lib.create_tables()
                sql_lib.load_admin_from_json(path_to_admin_json)
                sql_lib.load_standard_notify_from_file(path_to_notify_json)
                service_bot_logger.info('Инициализация успешна')
                return
            service_bot_logger.info('Инициализация не требуется, база создана.')
        except Exception as exc:
            service_bot_logger.error("Произошла ошибка при инициализации бота.", exc_info=True)


    def bot_commads(self):
        
        @self.bot.message_handler(commands=['дежурю'])
        @self.permissions_decorator
        def reqister_duty_engeneer(message):
            try:
                service_bot_logger.info(f'Запрос на установку дежурного с id {message.from_user.id}')
                sql_lib.set_owner_or_duty_db(message.from_user.id)
                # set_duty_phone(return_phone_num_db(message.from_user.id))
                self.bot.send_message(message.from_user.id, f'Успешно установлен новый дежурный {message.from_user.id}')
            except Exception as exc:
                service_bot_logger.error(f'Ошибка при установке дежурного {exc}')
                self.bot.send_message(message.from_user.id, 'Не удалось установить нового дежурного')

    def run(self):
        try:
            service_bot_logger.info('Запускаем бота')
            self.bot_commads()
            self.bot.polling(none_stop=True, interval=0, timeout=20)
        except ValueError as perm_exc:
            service_bot_logger.error('Произошла ошибка прав доступа', exc_info=True)
        except Exception as exc:
            service_bot_logger.error(f'Ошибка при запуске бота', exc_info=True)
        