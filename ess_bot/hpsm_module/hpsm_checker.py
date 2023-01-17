from json import loads 
from time import sleep
from datetime import datetime
from threading import Thread
import telebot
from selenium import webdriver
from ..logger_config.logger_data import create_logger
from ..sqlite_module.sql_lib import get_owner_or_duty_db, write_hpsm_status_db
from ..bot_exceptions.hpsm_exceptions import *
from .hpsm_config import *

#configure logger
hpsm_logger = create_logger(__name__)


class Hpsm_checker(Thread):

    def __init__(self,bot_token:str,rr_file_path,request_codes_file_path,*args,**kwargs):
        super().__init__(*args, **kwargs)
        self.bot_token = bot_token
        self.rr_file_path = rr_file_path
        self.request_codes_file_path = request_codes_file_path
        self.rr_list = []
        self.request_codes = []


    def create_bot(self):
        bot = telebot.TeleBot(self.bot_token, parse_mode='MARKDOWN')
        return bot


    def send_notification(self,text,channel=False,duty=False,owner=False,screeshot=False):
        bot = self.create_bot()
        duty = get_owner_or_duty_db(role='duty')
        owner = get_owner_or_duty_db(role='owner')
        keyboard = None
        if screeshot:
            bot.send_photo(duty['tg_id'],photo=open('screenshot_hpsm.jpg','rb'))
            bot.send_photo(owner['tg_id'],photo=open('screenshot_hpsm.jpg','rb'))
        bot = self.create_bot()
        if channel:
            bot.send_message(ESS_CHAT_ID,text+f"\n[{duty['fio']}](tg://user?id={duty['tg_id']})\n[{owner['fio']}](tg://user?id={owner['tg_id']})")
        if duty:
            bot.send_message(duty['tg_id'],text,reply_markup=keyboard)
        if owner:
            bot.send_message(owner['tg_id'],text)


    def make_screenshot(self):
        driver = self.create_webdriver()
        driver.get(HPSM_PAGE)
        self.login_hpsm(driver)
        self.wait_for_frame(driver, 80)
        try:
            driver.get_screenshot_as_file("screenshot_hpsm.jpg")
        except Exception as exc:
            hpsm_logger.error('Произошла ошибка при получении скриншота.', exc_info=True)
            raise HpsmScreenshotError
        driver.get('https://hpsm.emias.mos.ru/sm/goodbye.jsp?lang=')
        driver.quit()
    

    def check_tickets_for_notification(self,tickets):
        hpsm_logger.info('проверяем заявки на необходимость уведомления')
        current_hour = datetime.now().strftime("%H")
        current_min = datetime.now().strftime("%M")
        ignore_statuses = ['В работе','Отложен','Ожидание','Подготовка Отчета']
        message_for_get_request = """Заявка [{ticket_id}](https://hpsm.emias.mos.ru/sm/index.do?lang=) не взята в работу!"""
        message_with_rr_count = """В работе осталось {rr_count} не закрытых РР!"""
        hpsm_logger.info(f'Проверяем заявки на соответствие времени уведомлений {current_hour} : {current_min}.')
        for ticket in tickets:
            if self.check_working_time() and ticket['status'] not in ignore_statuses and not(ticket['record_id'].startswith('C') or ticket['record_id'].startswith('T')):
                hpsm_logger.info(f'Отправляем уведомление по заявке {ticket["record_id"]}')
                self.send_notification(text=message_for_get_request.format(ticket_id=ticket['record_id']),channel=True,
                owner=True,duty=True)
        rr_counter = self.get_rr_count(tickets=tickets)['rr_task_count']
        hpsm_logger.info(f'Кол-во РР = {rr_counter} сработка условий- '+ str(int(current_hour) == 17 and int(current_min) > 30) and rr_counter != 0 and self.check_working_time())
        if (int(current_hour) == 17 and int(current_min) > 30) and rr_counter != 0 and self.check_working_time():
            hpsm_logger.warning(f'Отправляем уведомление по открытым РР {rr_counter}')
            self.send_notification(text=message_with_rr_count.format(rr_count=rr_counter), channel=True)
        
        if int(current_hour) == 17 and int(current_min) > 45 and rr_counter != 0 and self.check_working_time():
            hpsm_logger.warning(f'Делаем скриншот hpsm. Время снятия - {current_hour} : {current_min}.')
            self.make_screenshot()
       

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


    def load_request_codes_from_file(self):
        with open(self.request_codes_file_path, 'r', encoding='utf8') as request_code_file:
            for line in request_code_file:
                self.request_codes.append(line.strip())


    def load_rr_from_file(self):
        with open(self.rr_file_path, 'r', encoding='utf8') as rr_file:
            for line in rr_file:
                self.rr_list.append(line.strip())


    def wait_for_frame(self,webdriver,timeout):
        try_counter = 1
        hpsm_logger.info('Делаем паузу для загрузки страницы')
        while try_counter < timeout:

            try:
                webdriver.switch_to.frame(webdriver.find_element_by_tag_name('iframe'))
            except KeyboardInterrupt as exc:
                hpsm_logger.error('Операция прервана пользователем')
                webdriver.get(HPSM_EXIT_PAGE)
                webdriver.close()
            except Exception as exc:
                hpsm_logger.info(f"Элемент iframe не обнаружен попытка №{try_counter}")
                sleep(1)
                try_counter += 1
                continue
            else:
                sleep(2)
                hpsm_logger.info(f'Количество попыток для получения списка заявок - {try_counter}')
                break
        else:
            hpsm_logger.error('Фрейм с заявками не найден')
            webdriver.get(HPSM_EXIT_PAGE)
            webdriver.quit()
            raise GetHpsmFrameException


    def login_hpsm(self,webdriver):
        hpsm_logger.info('Логинимся с учеткой - '+ HPSM_USER)
        try:
            hpsm_logger.info('Добавляем cookie на кол-во строк в странице = 50')
            webdriver.add_cookie({'name':'pagesize','value':'50'}) 
            webdriver.find_element_by_id('LoginUsername').send_keys(HPSM_USER)
            webdriver.find_element_by_id('LoginPassword').send_keys(HPSM_PASS)
            webdriver.find_element_by_id('loginBtn').click()
            return webdriver
        except Exception as exc:
            webdriver.quit()
            hpsm_logger.error(f'Произошла ошибка при логине с учетными данными {HPSM_USER}',exc_info=True)
            print(exc.args)
            raise HpsmLoginException


    def get_html_page(self, webdriver):
        hpsm_logger.info(f'Запрашиваем страницу {HPSM_PAGE}')
        
        try:
            webdriver.get(HPSM_PAGE)
        except Exception as exc:
            webdriver.quit()
            hpsm_logger.error(f'Произошла ошибка в запросе страницы {HPSM_PAGE}', exc_info=True)
            raise GetPageException
        
        webdriver_login = self.login_hpsm(webdriver)
        self.wait_for_frame(webdriver_login, 80)
        hpsm_html = webdriver_login.page_source
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

        for replace_elem in self.request_codes:
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
        return {'rr_task_count':rr_counter, 'task_count': (len(tickets)-rr_counter)}


    def run(self):
        while True:
            try:
                self.load_rr_from_file()
                self.load_request_codes_from_file()
                source = self.get_html_page(webdriver=self.create_webdriver()) 
                tickets = self.parse_hpsm_html(source)
                self.check_tickets_for_notification(tickets=tickets)
                hpsm_logger.info('Записываем данные о заявках из HPSM в БД')
                write_hpsm_status_db(**self.get_rr_count(tickets))
            except GetHpsmFrameException as exc:
                hpsm_logger.error('Произошла ошибка при получении заявок с HPSM.')
                self.send_notification(text=f'Ошибка при получении заявок с HPSM следующая попытка через {HPSM_CHECK_INTERVAL_SECONDS} секунд.', channel=True)
            except EmptyRequestsListReturn as exc:
                hpsm_logger.warning('Вернулся пустой список задач с HPSM.')
                print(exc,exc.args)
            except HpsmScreenshotError as exc:
                self.send_notification('Ошибка в получении скриншота HPSM, необходимо сделать скриншот в ручную.')
            except Exception as exc:
                print(exc,exc.args)
                hpsm_logger.error('Возникло необрабатываемое исключение',exc_info=True)
                self.send_notification(text=f'Возникло необработанное исключение во время работы с заявками',channel=True)
            finally:
                sleep(HPSM_CHECK_INTERVAL_SECONDS)
