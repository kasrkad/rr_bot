import sys
sys.path.append('../')
import logging
import telebot
from sqlite_module import sql_lib
from asterisk_module import asterisk_lib
from config import *
import os
from keyboards import keyboards

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
        self.main_menu_call_data = ['contacts','help','admin_menu']
        self.admin_menu_call_data = ['producer','set_owner_manual','duty']

    
    def permissions_decorator(self,func_for_decorate):
        def wrapper(message):
            if sql_lib.check_admin_permissions(message.from_user.id):
                func_for_decorate(message)
            else:
                self.bot.send_message(message.from_user.id,'В доступе отказано.')
                service_bot_logger.error(f'У пользователя с id {message.from_user.id} нет прав доступа.')
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


        @self.bot.message_handler(commands=['start'])
        def start_command(message):
            service_bot_logger.info(f'Инициировано главное меню')
            try:
                self.bot.send_message(message.from_user.id,'Меню', reply_markup=keyboards.main_menu_keyboard)
            except Exception as exc:
                service_bot_logger.error(f'Ошибка при отображении главного меню')


        @self.bot.message_handler(commands=['help'])
        def help_command(message):
            self.bot.send_message(message.from_user.id,"""Команды
/help - это сообщение,
/adminPanel - панель администратора,
/contacts - контакты дежурного и координатора по СИМИ,ОНКО,СЭМД 
""")

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
        

        @self.bot.message_handler(commands=['admins'])
        @self.permissions_decorator
        def show_all_admins(message):

            service_bot_logger.info(f'Запрос на отображение админов от {message.from_user.id} ')
            try:
                admins_for_show = sql_lib.show_all_admin_db()
                self.bot.send_message(message.from_user.id,"\n".join(admin for admin in admins_for_show.values()))
            except Exception as exc:
                service_bot_logger.error(f'Произошла ошибка при запросе админов от {message.from_user.id}', exc_info=True)


        @self.bot.message_handler(commands=['set_owner_manual'])
        @self.permissions_decorator
        def set_owner_dialogue(message):

            service_bot_logger.info(f'От {message.from_user.id} запрошено ручное переключение руководителя группы.')
            try:
                show_all_admins(message)
                message_for_set_duty = self.bot.send_message(message.from_user.id,'Введите телеграм ID для установки ответственного за HPSM в ручную')
                self.bot.register_next_step_handler(message_for_set_duty, set_owner_manual)
            except Exception as exc:
                self.bot.send_message(message.from_user.id,'Произошла ошибка в диалоге.')
                service_bot_logger.error(f'Произошла ошибка в диалоге установки руководителя группы в ручную от {message.from_user.id}.', exc_info=True)
    

        def set_owner_manual(message):

            try:
                current_owner = sql_lib.get_owner_or_duty_db(role='owner')
                if current_owner:
                    self.bot.send_message(message.from_user.id, f'Предыдущий ответственный за HPSM [{current_owner["fio"]}](tg://user?id={current_owner["tg_id"]})')
                else:
                    self.bot.send_message(message.from_user.id, 'Предыдущий ответственный за HPSM не обнаружен.')
                sql_lib.set_owner_or_duty_db(message.text.strip(), role='owner')
                new_owner = sql_lib.get_owner_or_duty_db(role='owner')
                self.bot.send_message(message.from_user.id,f'Новый ответственный за HPSM - [{new_owner["fio"]}](tg://user?id={new_owner["tg_id"]})')

            except Exception as exc:
                self.bot.send_message(message.from_user.id,'Произошла в установке нового ответственного.')
                service_bot_logger.error(f'Произошла ошибка при установке HPSM_owner = {message.text}', exc_info=True)
            

        @self.bot.message_handler(commands=['/producer'])
        @self.permissions_decorator
        def producer_recreate(message):
            service_bot_logger.info(f'Запрошено пересоздание продюсера')
            try:
                self.bot.send_message(message.from_user.id,'Запущено пересоздание продюсера.')
                print('agressive recreating')
                self.bot.send_message(message.from_user.id, 'Пересоздание завершено.')
            except Exception as exc:
                service_bot_logger.error(f'Произошла ошибка при пересоздании продюсера, запрос от {message.from_user.id}.', exc_info=True)

        @self.bot.message_handler(commands=['contacts'])
        def get_contacts(message):
            service_bot_logger.info(f'Пользователем {message.from_user.id} запрошены контакты.')
            try:
                current_duty = sql_lib.get_owner_or_duty_db(role='duty')
                current_owner = sql_lib.get_owner_or_duty_db(role='owner')
                if current_duty and current_owner:
                    self.bot.send_message(message.from_user.id,f'''Дежурный инженер СИМИ,ОНКО,СЭМД - [{current_duty["fio"]}](tg://user?id={current_duty["tg_id"]})
Координатор СИМИ,ОНКО,СЭМД - [{current_owner["fio"]}](tg://user?id={current_owner["tg_id"]})''')
            except Exception as exc:
                self.bot.send_message(message.from_user.id, f'Произошла ошибка при запросе контактов.')
                service_bot_logger.error(f'Произошла ошибка при запросе контактов от {message.from_user.id}', exc_info=True)


        @self.bot.message_handler(commands=['/adminPanel'])
        @self.permissions_decorator
        def show_admin_panel(message):
            service_bot_logger.info(f'Открыта админ панель для пользователя {message.from_user.id}')
            try:
                self.bot.send_message(message.from_user.id,f'Открыта админ панель.', reply_markup=keyboards.admin_menu_keyboard)
            except Exception as exc:
                service_bot_logger.error(f'Произошла ошибка при открытии административной панели для {message.from_user.id}')
                self.send_message(message.from_user.id,'Произошла ошибка при открытии административной панели.')

        @self.bot.callback_query_handler(func=lambda call: call.data in self.main_menu_call_data)
        def callback_inline(call):
            if call.data == 'admin_menu':
                show_admin_panel(call)
            if call.data == 'help':
                help_command(call)
            if call.data == 'contacts':
                get_contacts(call)

        @self.bot.callback_query_handler(func=lambda call: call.data in self.admin_menu_call_data)
        def callback_inline(call):
            if call.data == 'set_owner_manual':
                set_owner_dialogue(call)
            if call.data == 'duty':
                reqister_duty_engeneer(call)
            if call.data == 'producer':
                producer_recreate(call)

    def run(self):
        try:
            service_bot_logger.info('Запускаем бота')
            self.bot_commads()
            self.bot.polling(none_stop=True, interval=0, timeout=20)
        except Exception as exc:
            service_bot_logger.error(f'Ошибка при запуске бота', exc_info=True)
        