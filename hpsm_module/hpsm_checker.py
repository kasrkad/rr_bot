from json import loads 
from config import ESS_CHAT_ID, HPSM_REPLACE
from sys import path
from time import sleep
from datetime import datetime
from os import environ
import logging
import telebot
from selenium import webdriver
from threading import Thread
path.append('../')
from sqlite_module.sql_lib import get_owner_or_duty_db, write_hpsm_status_db
from bot_exceptions.hpsm_exeptions import *

#get env's
HPSM_PAGE = environ["HPSM_PAGE"]
HPSM_EXIT_PAGE = environ["HPSM_EXIT_PAGE"]
HPSM_USER = environ["HPSM_USER"]
HPSM_PASS = environ["HPSM_PASS"]
HPSM_CHECK_INTERVAL_SECONDS = int(environ["HPSM_CHECK_INTERVAL_SECONDS"])

#configure logger
hpsm_logger = logging.getLogger('hpsm_logger')
hpsm_logger_formatter = logging.Formatter(
    "%(name)s %(asctime)s %(levelname)s %(message)s")
hpsm_logger.setLevel(logging.INFO)
hpsm_logger_logger_handler_file = logging.FileHandler("./logs/hpsm_logger.log", 'a')
hpsm_logger_logger_handler_file.setLevel(logging.INFO)
hpsm_logger_logger_handler_file.setFormatter(hpsm_logger_formatter)
hpsm_logger.addHandler(hpsm_logger_logger_handler_file)

class Hpsm_checker(Thread):

    def __init__(self,bot_token:str,rr_file_path,*args,**kwargs):
        super().__init__(*args, **kwargs)
        self.bot_token = bot_token
        self.rr_file_path = rr_file_path
        self.rr_list = []

    def send_notification_to_channel(self,text):
        bot = telebot.TeleBot(self.bot_token, parse_mode='MARKDOWN')
        duty = get_owner_or_duty_db(role='duty')
        owner = get_owner_or_duty_db(role='owner')      
        bot.send_message(ESS_CHAT_ID,text+f"\n[{duty['fio']}](tg://user?id={duty['tg_id']})\n[{owner['fio']}](tg://user?id={owner['tg_id']})")
        bot.send_message(duty['tg_id'],text)
        bot.send_message(owner['tg_id'],text)

    def send_notification(self,ticket_id,regular_work_count=None):
        bot = telebot.TeleBot(self.bot_token, parse_mode='MARKDOWN')
        if regular_work_count:
            hpsm_logger.info('Отправляем уведомление о кол-ве активных регламентных работ.')
            bot.send_message(ESS_CHAT_ID,f'Внимание, кол-во не закрытых РР = {regular_work_count}!')
            return

        hpsm_logger.info(f'Отправляем уведомление о заявке {ticket_id}')
        owner = get_owner_or_duty_db(role='owner')
        duty = get_owner_or_duty_db(role='duty')

        try:
            bot.send_message(ESS_CHAT_ID,f"""Заявка [{ticket_id}](https://hpsm.emias.mos.ru/sm/index.do?lang=) не взята в работу! Вызываем ответственных:
    [{duty['fio']}](tg://user?id={duty['tg_id']})\n[{owner['fio']}](tg://user?id={owner['tg_id']})""")
            return
        except Exception as exc:
            hpsm_logger.error(f'Произошла ошибка при отправке уведомления {ticket_id}')


    def check_tickets_for_notification(self,tickets):
        hpsm_logger.info('проверяем заявки на необходимость уведомления')
        current_hour = datetime.now().strftime("%H")
        current_min = datetime.now().strftime("%M")
        ignore_statuses = ['В работе','Отложен','Ожидание','Подготовка Отчета']
        message_for_get_request = """Заявка [{ticket_id}](https://hpsm.emias.mos.ru/sm/index.do?lang=) не взята в работу!"""
        message_with_rr_count = """В работе осталось {rr_count} не закрытых РР!"""
        hpsm_logger.info('Проверяем заявки на соответствие времени уведомлений.')
        for ticket in tickets:
            if self.check_working_time() and ticket['status'] not in ignore_statuses:
                hpsm_logger.info(f'Отправляем уведомление по заявке {ticket["status"]}')
                self.send_notification_to_channel(text=message_for_get_request.format(ticket_id=ticket['record_id']))
        rr_counter = self.get_rr_count(tickets=tickets)['rr_task_count']

        if int(current_hour) == 17 and int(current_min) > 30 and rr_counter != 0 and self.check_working_time():
            hpsm_logger.warning(f'Отправляем уведомление по открытым РР {rr_counter}')
            self.send_notification_to_channel(text=message_with_rr_count.format(rr_count=rr_counter))

    def create_webdriver(self):
        hpsm_logger.info('Создаем драйвер')
        options = webdriver.FirefoxOptions()
        options.add_argument('--headless')
        driver = webdriver.Firefox(executable_path='./geckodriver', options=options)
        driver.set_window_size(1920, 1080)
        return driver


    def check_working_time(self):
        work_hours = datetime.now()
        hours = int(work_hours.strftime("%H"))
        week_day =  datetime.today().weekday()
        if hours >= 10 and hours < 22 and week_day != 6:
            return True
        return False


    def load_rr_from_file(self):
        with open(self.rr_file_path, 'r', encoding='utf8') as rr_file:
            for line in rr_file:
                self.rr_list.append(line.strip())


    def get_html_page(self, webdriver):
        hpsm_logger.info(f'Запрашиваем страницу {HPSM_PAGE}')
        
        try:
            webdriver.get(HPSM_PAGE)
        except Exception as exc:
            webdriver.quit()
            hpsm_logger.error(f'Произошла ошибка в запросе страницы {HPSM_PAGE}', exc_info=True)
            raise GetPageException
        
        hpsm_logger.info('Добавляем cookie на кол-во строк в странице = 50')
        webdriver.add_cookie({'name':'pagesize','value':'50'})
        hpsm_logger.info(f'Логинимся в HPSM с учетными данными {HPSM_USER}')
        
        try:
            webdriver.find_element_by_id('LoginUsername').send_keys(HPSM_USER)
            webdriver.find_element_by_id('LoginPassword').send_keys(HPSM_PASS)
            webdriver.find_element_by_id('loginBtn').click()
        except Exception as exc:
            webdriver.quit()
            hpsm_logger.error(f'Произошла ошибка при логине с учетными данными {HPSM_USER}')
            raise HpsmLoginException

        hpsm_logger.info('Делаем паузу для загрузки страницы')
        try_counter = 1
        while try_counter < 80:

            try:
                webdriver.switch_to.frame(webdriver.find_element_by_tag_name('iframe'))
            except KeyboardInterrupt as exc:
                hpsm_logger.error('Операция прервана пользователем')
                webdriver.get(HPSM_EXIT_PAGE)
                webdriver.close()
            except Exception as exc:
                hpsm_logger.info(f"Элемент iframe не обнаружен попытка №{try_counter}")
                sleep(2)
                try_counter += 1
                continue
            else:
                sleep(2)
                break
        else:
            hpsm_logger.error('Фрейм с заявками не найден ')
            self.send_notification_to_channel(text=f'Заявки с HPSM не получены!!\nСледующая попытка через {HPSM_CHECK_INTERVAL_SECONDS} секунд.')
            webdriver.get(HPSM_EXIT_PAGE)
            webdriver.quit()
            raise GetHpsmFrameException
            
        hpsm_logger.info(f'Количество попыток для получения списка заявок - {try_counter}')
        hpsm_html = webdriver.page_source
        webdriver.get(HPSM_EXIT_PAGE)
        webdriver.close()
        hpsm_logger.info('Драйвер и соединение закрыто.')
        return hpsm_html

    
    def parse_hpsm_html(self, html_source):
        start_string = 'var listConfig = '
        end_string = 'columns: ['
        tickets_keys = ['record_id','itemType','description','status','group','priority']
        ready_tickets = []
        raw_tickets = html_source[html_source.index(start_string)+len(start_string)+13:html_source.index(end_string)-8]

        for replace_elem in HPSM_REPLACE:
            raw_tickets = raw_tickets.replace(replace_elem,"")
        data_tickets = loads(raw_tickets)['model']['instance']
            
        for ticket in data_tickets:
            new_ticket = {}
            for key,value in ticket.items():
                if key in tickets_keys:
                    if key == 'priority':
                        value = value.split(" ")[0]
                    new_ticket[key] = value
            ready_tickets.append(new_ticket)
        
        if ready_tickets:
            return ready_tickets
        raise EmptyRequestsListReturn('Вернулся пустой список заявок')


    def get_rr_count(self, tickets):
        rr_counter = 0
        for ticket in tickets:
            if ticket['description'] in self.rr_list:
                rr_counter+=1
        return {'rr_task_count':rr_counter, 'task_count': len(tickets)-rr_counter}


    def run(self):
        while True:
            try:
                self.load_rr_from_file()
                source = self.get_html_page(webdriver=self.create_webdriver()) 
                tickets = self.parse_hpsm_html(source)
                self.check_tickets_for_notification(tickets=tickets)
                hpsm_logger.info('Записываем данные о заявках из HPSM в БД')
                write_hpsm_status_db(self.get_rr_count(tickets))
            except EmptyRequestsListReturn as e:
                hpsm_logger.warning('Вернулся пустой список задач с HPSM.')
                print(e)
            except Exception as exc:
                print(exc)
                hpsm_logger.error('Возникло необрабатываемое исключение',exc_info=True)
                #отправка уведомления 
            finally:
                sleep(HPSM_CHECK_INTERVAL_SECONDS)
 