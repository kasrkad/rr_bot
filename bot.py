import telebot
import sys
import os
import json
from subprocess import Popen, PIPE
from config import *
from artifacts import *
import re
import requests


class ECC_telegram_bot:


    def __init__(self, bot_token):
        self.bot = telebot.TeleBot(bot_token, parse_mode='MARKDOWN')
        self.duty_engeneer = {}
        self.valid_users = {}
        self.hpsm_checker = None
        self.document_download_pattern = r"[a-z0-9]{8}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{12}"


    def load_duty_and_users(self):
        """
        [Грузим админов и дежурного, если дежурного нет, дежурным становится А.Бауман]
        """
        if os.path.exists('duty.json'):
            with open('duty.json', 'r', encoding='utf8') as duty_file:
                self.duty_engeneer = json.load(duty_file)
        else:
            self.duty_engeneer = {"t_id":753785354,"first_name": "Александр", "last_name": "Бауман"}
            self.bot.send_message(ECC_CHAT_ID, f"Дежурный не зарегистрирован, {DUTY_OWNER} выбирай дежурного!")
            with open('duty.json', 'w', encoding='utf8') as duty_file:
                json.dump(self.duty_engeneer, duty_file, ensure_ascii=False)

        if os.path.exists('users.json'):
            with open('users.json', 'r', encoding='utf8') as users_file:
                self.valid_users = json.load(users_file)
        else:
            self.bot.send_message(ECC_CHAT_ID, "Не обнаружен файл с администраторами, доступ к функциям бота заблокирован")

    def check_permission(self, message):
        """
        Проверяем доступ к функциям бота по tg_id
        нет доступа кидаем исключение
        Raises:
            ValueError: [description]
        """
        if str(message.from_user.id) not in self.valid_users.keys():
            raise ValueError(f"{message.from_user.last_name} {message.from_user.first_name} не имеет право давать боту комманды")

    
    def download_document(self, id_, tg_user_id):
        """
        Скачивает док с ППАК, если дока с таким ИД нет, вернется файл со стектрейсом
        Args:
            id_ ([str]): ИД документа для скачивания
            tg_user_id ([str]): телеграм id пользователя скачивающего документ
        """
        id_ = id_.rstrip()
        body = REQUEST_BODY.format(id=id_, tg=tg_user_id, PPAK_SOAP_USER=PPAK_SOAP_USER)
        headers = {'content-type': 'text/xml'}
        response = requests.post(PPAK_SOAP_URL, data=body, headers=headers)
        with open("./docs/documents_output/" + id_ + ".xml", "wb+") as id_file:
            id_file.write(response.text.encode('utf-8').strip())
    
    
    def start_hpsm_checker(self):
        """
        Запускает в отдельном процессе отслеживание заявок в HPSM
        """
        self.hpsm_checker = Popen(['python3','rr_bot.py'], stdout=PIPE, stderr=PIPE)


    def change_duty_phone(self, t_id):
        """При регистрации дежурного переключаем номер на него.
    
        """
        payload = ASTERISK_PAYLOAD
        phones = list(self.valid_users[str(t_id)].values())[0]
        print(phones)
        payload['grplist'] = f'{phones}#'
        ring_reload = {"handler": "reload"}
        print(payload)
        r = requests.Session()
        auth = r.post('https://pbx/index.php',data=ASTERISK_LOGIN, verify=False)
        change_ring_group = r.post(ASTERISK_GROUP, data=payload,cookies=r.cookies,headers=ASTERSK_HEADERS, verify=False, allow_redirects=True)
        reload_group_settings = r.post(ASTERISK_GROUP, data=ring_reload, verify=False)
   

    def restart_bot(self):
        """
        Перезапускает бота включая мониторинг заявок
        """
        self.hpsm_checker.terminate()
        kill_gecko = Popen(['pkill','geckodriver'], stdout=PIPE, stderr=PIPE)
        kill_gecko.wait()
        os.sys.stdout.flush()
        os.execv(sys.executable, ['python3'] + sys.argv)


    def bot_commands(self):
        """
        Вызывается чтобы подсунуть боту команды которые он должен обрабатывать
        """


        @self.bot.message_handler(commands=['загрузи'])
        def load_artifact(message):
            try:
                self.check_permission(message)
                handler = Cct_message_handler_loader(self.bot)
                handler.target_stand_set(message)
            except ValueError as valexc:
                print(valexc)
                self.bot.reply_to(message,"some shit was happen")
                        
        @self.bot.message_handler(commands=['перенеси'])
        def load_artifact(message):
            try:
                self.check_permission(message)
                handler = Cct_message_hander_mover(self.bot)
                handler.source_stand_set(message)
            except ValueError as valexc:
                self.bot.reply_to(message,valexc.args[0])

        @self.bot.message_handler(commands=['status'])
        def status_report(message):
            try:
                self.check_permission(message)
                if os.path.exists('last_check.json'):
                    with open('last_check.json', 'r', encoding='utf8') as json_check:
                        check_status = json.load(json_check)
                        self.bot.reply_to(message, f'''Дежурный - [{self.duty_engeneer["first_name"]} {self.duty_engeneer["last_name"]}](tg://user?id={self.duty_engeneer["t_id"]}).
Последняя проверка - {check_status["check_time"]}.
Кол-во активных заявок - {check_status["tickets_count"]}.
Время между проверками заявок {int(HPSM_CHECK_INTERVAL_SECONDS)//60} мин.
                              ''')
                else:
                    self.bot.reply_to(message, "Невозможно получить данные о последней проверке, возможно необходим перезапуск.")
            except ValueError as valexc:
                self.bot.reply_to(message, valexc.args[0])
            except Exception as others:
                print(others)
           

        @self.bot.message_handler(commands=['дежурю', 'Дежурю', 'Дежурный', 'дежурный'])
        def register_duty_engeneer(message):
            try:
                self.check_permission(message)
                self.bot.send_message(ECC_CHAT_ID,f'Дежурный зарегистрирован - [{message.from_user.first_name} {message.from_user.last_name}](tg://user?id={message.from_user.id}), номер переключен')
                self.bot.send_message(ECC_CHAT_ID,f'Предыдущий дежурный - [{self.duty_engeneer["first_name"]} {self.duty_engeneer["last_name"]}](tg://user?id={self.duty_engeneer["t_id"]})')
                self.duty_engeneer = {"t_id": message.from_user.id, "first_name": message.from_user.first_name, "last_name": message.from_user.last_name}
                self.change_duty_phone(message.from_user.id)
                with open('duty.json', 'w', encoding='utf8') as duty_file:
                    json.dump(self.duty_engeneer, duty_file, ensure_ascii=False)
            except ValueError as exc:
                self.bot.reply_to(exc.args[0])
            except Exception as others:
                print(f'{others}')


        @self.bot.message_handler(commands=['help'])
        def help_print(message):
            self.bot.reply_to(message,"""/help - покажу это сообщение,
/дежурю - регистрирую как дежурного, переключаю телефон на дежурного,
/status - покажу дежурного и статус заявок,
/загрузи - грузим на стенд из списка сст по коммиту,
/перенеси - перенос сст со стенда на стенд
Пришли мне текст с ID документа SIMI, скачаю и отправлю его в ответ.
""")

        @self.bot.message_handler(commands=['restart'])
        def restart(message):
            try:
                self.check_permission(message)
                self.bot.reply_to(message,"Бот перезапускается")
                self.restart_bot()
            except ValueError as exc:
                self.bot.reply_to(exc.args[0])
            except Exception as others:
                print(others)


        @self.bot.message_handler(regexp=self.document_download_pattern)
        def handle_message(message):
            try:
                self.check_permission(message)
                docs_from_forward = re.findall(self.document_download_pattern, message.text)
                for doc in docs_from_forward:
                    with open('./docs/doc_download_log/log.txt', 'a', encoding='utf8') as doc_log:
                        doc_log.write(f"{doc} скачан пользователем {message.from_user.first_name} {message.from_user.last_name} - id {message.from_user.id}\n")
                    self.download_document(doc, message.from_user.id)
                    document = open(f'./docs/documents_output/{doc}.xml')
                    self.bot.send_document(message.from_user.id, document)
                    os.remove(f'./docs/documents_output/{doc}.xml')
            except ValueError as exc:
                self.bot.reply_to(message, exc.args[0])


    def run(self):
        try:
            if HTTP_PROXY:
                telebot.apihelper.proxy = {"http": HTTP_PROXY}
            self.load_duty_and_users()
            self.bot_commands()
            self.start_hpsm_checker()
            self.bot.send_message('1739060486', "Бот запущен")
            self.bot.polling(none_stop=True, interval=0, timeout=20)
        except Exception as exc:
            print(exc)
            with open('t_bot.log', 'a', encoding='utf8') as t_bot_log:
                t_bot_log.write(",".join(str(arg) for arg in exc.args)+"\n")
            self.restart_bot()


if __name__=='__main__':
    
    bot = ECC_telegram_bot(TG_BOT_TOKEN)
    bot.run()
