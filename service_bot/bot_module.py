import sys
sys.path.append('../')
import telebot
from sqlite_module import sql_lib
from asterisk_module import asterisk_lib
from config import *
import os
from keyboards import keyboards
import re
from simi_requests_module.bot_soap_requests import *
from simi_requests_module.request_to_simi import *
from oracle_module import oracle_lib
from logger_config.logger_data import create_logger

#configure logger
service_bot_logger =  create_logger(__name__)

class Ess_service_bot:

    
    def __init__(self, bot_token):
        self.bot = telebot.TeleBot(bot_token, parse_mode='MARKDOWN')
        self.document_regexp = r"[a-z0-9]{8}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{12}"
        self.main_menu_call_data = ['contacts','help','admin_menu','notify_get']
        self.admin_menu_call_data = ['producer','set_owner_manual','duty','notify_set_active']
        self.documents_call_data = ['download_doc_test','download_json_test','audit_test', 
                                    'status_test','download_doc_ppak','download_json_ppak',
                                    'audit_ppak','status_ppak'] 

    
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
            os.makedirs('logs',exist_ok=True)
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
                current_duty= sql_lib.get_owner_or_duty_db(role='duty')
                sql_lib.set_owner_or_duty_db(message.from_user.id)
                new_duty = sql_lib.get_owner_or_duty_db(role='duty')
                # set_duty_phone(return_phone_num_db(message.from_user.id))
                self.bot.send_message(message.from_user.id, f'Предыдущий дежурный - [{current_duty["fio"]}](tg://user?id={current_duty["tg_id"]}),\nновый дежурный - [{new_duty["fio"]}](tg://user?id={new_duty["tg_id"]})')
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
            

        def send_file(tg_id,files:list):
            if files:
                for file in files:
                    doc = open(file)
                    self.bot.send_document(tg_id,doc)
                    doc.close()
                    os.remove(file)
            else:
                raise ValueError

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

        @self.permissions_decorator
        @self.bot.message_handler(commands=['/notify_get'])
        def notify_get(message):
            service_bot_logger.info(f'Пользователем {message.from_user.id} запрошены уведомления.')
            try:
                notifys = sql_lib.get_all_notifys()
                message_with_notifys = ""
                for notify in notifys:
                    message_with_notifys += f"id: {notify[0]}\nИмя: {notify[1]}\nВремя срабатывания: {notify[2]}\nДни недели: {notify[3]}\nПользовательское/системное: {notify[5]}\nАктивное: {notify[7]}\n\n"
                if message_with_notifys:
                    self.bot.send_message(message.from_user.id, "Список доступных уведомлений.")
                    self.bot.send_message(message.from_user.id, message_with_notifys, parse_mode="HTML")
                    return
                self.bot.send_message(message.from_user.id,'Уведомлений не обнаружено' )
            except Exception as exc:
                self.bot(message.from_user.id,f'Произошла ошибка при запросе уведомлений.')
                service_bot_logger.error(f'Произошла ошибка при запросе уведомлений от {message.from_user.id}', exc_info=True)


        @self.permissions_decorator
        @self.bot.message_handler(commands=['/change_notify_status'])
        def change_notify_status_dialogue(message):
            service_bot_logger.info(f'Пользовтелем {message.from_user.id} запрошено изменение состояния уведомления.')
            notify_get(message)
            message_for_set_status = self.bot.send_message(message.from_user.id, 'Введите id уведомлений, и желаемый статус(on/off), через : .Пример - 1:off')
            self.bot.register_next_step_handler(message_for_set_status, set_notify_status)

        def set_notify_status(message):
            service_bot_logger.info(f'Меняем статус {message.text}')
            notify_id, active = message.text.strip().split(':')
            if active == 'off':
                active = False
            else:
                active = True
            try:
                sql_lib.set_notify_active(notify_id=notify_id,active=active)
                self.bot.send_message(message.from_user.id,f'Статус уведомления успешно изменен.')
            except Exception as exc:
                service_bot_logger.info(f'Произошла ошибка при изменении состояния уведомления {message.text}')
                self.bot.send_message(message.from_user.id,f'Произошла ошибка при изменении состояния уведомления.')



        @self.bot.message_handler(regexp=self.document_regexp)
        def document_handle(message):
            global finded_docs 
            finded_docs = re.findall(self.document_regexp, message.text.strip())
            if sql_lib.check_admin_permissions(message.from_user.id):
                self.bot.send_message(message.from_user.id,f'Админские права подтверждены, выберите действие над документом', 
                                        reply_markup=keyboards.document_keyboard_admin)
            else:
                self.bot.send_message(message.from_user.id,'Админские права не подтверждены, доступен только стенд ТЕСТ',
                                        reply_markup=keyboards.document_keyboard_user)
            
            @self.bot.callback_query_handler(func=lambda call: call.data in self.documents_call_data)
            def callback_inline(call):
                try:
                    global finded_docs
                    self.bot.edit_message_text(
                        chat_id=call.message.chat.id, message_id=call.message.message_id, text="Запрашиваю документы.")
                    if call.data == 'download_doc_test':
                        doc_data_test = simi_document_request(request_to_simi=SIMI_GET_DOC_REQUEST, stand_node_adress=DEV_SOAP_URL,
                                                            documents_ids=finded_docs, requester_tg_id=call.from_user.id)
                        documents_for_send = write_json_or_xml_document(doc_data = doc_data_test)
                        send_file(tg_id=call.from_user.id, files=documents_for_send)
                    if call.data == 'download_json_test':
                        doc_data_json_test = base64_decode_to_json(request_to_convert=REQUEST_BASE64_TO_JSON_CONVERT, request_to_simi=SIMI_GET_DOC_REQUEST,
                                                                documents_ids=finded_docs, stand_node_adress=DEV_SOAP_URL, requester_tg_id=call.from_user.id)
                        documents_for_send = write_json_or_xml_document(doc_data=doc_data_json_test, file_format='json')               
                        send_file(tg_id=call.from_user.id, files=documents_for_send)
                    if call.data == 'audit_test':
                        audit_for_send = oracle_lib.get_audit_for_document(oracle_connection_string=DEV_DOC_CONNECTION_STRING, 
                                                                            documents=finded_docs)
                        send_file(tg_id=call.from_user.id, files=audit_for_send)
                    if call.data == 'status_test':
                        documents_with_statuses = oracle_lib.get_document_metadata_status(oracle_connection_string=DEV_DOC_CONNECTION_STRING,
                                                                                        documents=finded_docs)
                        for document, status in documents_with_statuses.items():
                            self.bot.send_message(call.from_user.id,f'{document}: {status}')
                    if call.data == 'download_doc_ppak':
                        doc_data_ppak = simi_document_request(request_to_simi=SIMI_GET_DOC_REQUEST,stand_node_adress=PPAK_SOAP_URL,
                        documents_ids=finded_docs,requester_tg_id=call.from_user.id)
                        documents_for_send = write_json_or_xml_document(doc_data = doc_data_ppak)
                        send_file(tg_id=call.from_user.id, files=documents_for_send)
                    if call.data == 'download_json_ppak':
                        doc_data_json_test = base64_decode_to_json(request_to_convert=REQUEST_BASE64_TO_JSON_CONVERT, request_to_simi=SIMI_GET_DOC_REQUEST,
                                                                documents_ids=finded_docs, stand_node_adress=PPAK_SOAP_URL, requester_tg_id=call.from_user.id)
                        documents_for_send = write_json_or_xml_document(doc_data=doc_data_json_test, file_format='json')               
                        send_file(tg_id=call.from_user.id, files=documents_for_send)
                    if call.data == 'audit_ppak':
                        audit_for_send = oracle_lib.get_audit_for_document(oracle_connection_string=PPAK_STANDBY_ORACLE_CONNECTION_STRING, 
                                                                            documents=finded_docs)
                        send_file(tg_id=call.from_user.id, files=audit_for_send)
                    if call.data == 'status_ppak':
                        documents_with_statuses = oracle_lib.get_document_metadata_status(oracle_connection_string=PPAK_STANDBY_ORACLE_CONNECTION_STRING,
                                                                                        documents=finded_docs)
                        for document, status in documents_with_statuses.items():
                            self.bot.send_message(call.from_user.id,f'{document}: {status}')

                except ValueError as val_error:
                    service_bot_logger.info(f'Пустой список документов')
                    self.bot.send_message(call.from_user.id,'Документы на стенде не обнаружены.')
                except Exception as exc:
                    service_bot_logger.error(f'Произошла ошибка при работе с документами', exc_info=True)
                    self.bot.send_message(call.from_user.id, 'Вовремя операции с документом произошла ошибка.')


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
            try:
                if call.data == 'admin_menu':
                    show_admin_panel(call)
                if call.data == 'help':
                    help_command(call)
                if call.data == 'contacts':
                    get_contacts(call)
                if call.data == 'notify_get':
                    notify_get(call)
            except Exception as exc:
                service_bot_logger.error('Во время операции произошла ошибка',exc_info=True)
                self.bot.send_message(call.from_user.id, 'Во время операции произошла ошибка')

        @self.bot.callback_query_handler(func=lambda call: call.data in self.admin_menu_call_data)
        def callback_inline(call):
            try:
                if call.data == 'set_owner_manual':
                    set_owner_dialogue(call)
                if call.data == 'duty':
                    reqister_duty_engeneer(call)
                if call.data == 'producer':
                    producer_recreate(call)
                if call.data == 'notify_set_active':
                    change_notify_status_dialogue(call)
            except Exception as exc:
                service_bot_logger.error(f'Во время операции произошла ошибка',exc_info=True)
                self.bot.send_message(call.from_user.id,'Во время операции произошла ошибка.')


    def run(self):
        try:
            service_bot_logger.info('Запускаем бота')
            self.bot_commads()
            self.bot.polling(none_stop=True, interval=0, timeout=20)
        except Exception as exc:
            service_bot_logger.error(f'Ошибка при запуске бота', exc_info=True)
        