import sys
from time import sleep
import os
import logging
import telebot
from selenium import webdriver
from threading import Thread
sys.path.append('../')
from sqlite_module.sql_lib import get_owner_or_duty_db
from bot_exceptions.hpsm_exeptions import GetHpsmFrameException,GetPageException,HpsmLoginException

#get env's
HPSM_PAGE = os.environ["HPSM_PAGE"]
HPSM_EXIT_PAGE = os.environ["HPSM_EXIT_PAGE"]
HPSM_USER = os.environ["HPSM_USER"]
HPSM_PASS = os.environ["HPSM_PASS"]
HPSM_CHECK_INTERVAL_SECONDS = int(os.environ["HPSM_CHECK_INTERVAL_SECONDS"])


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


    def create_webdriver(self):
        options = webdriver.FirefoxOptions()
        # options.add_argument('--headless')
        driver = webdriver.Firefox(executable_path='./geckodriver', options=options)
        driver.set_window_size(1920, 1080)
        return driver

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
        load_counter = 1
        while load_counter < 15:

            try:
                webdriver.switch_to.frame(webdriver.find_element_by_tag_name('iframe'))
            except Exception as exc:
                print(f'попытка - {load_counter}',exc)
                hpsm_logger.info(f"Элемент iframe не обнаружен попытка №{load_counter}")
                sleep(1)
                load_counter += 1
                continue
            else:
                sleep(1)
                break
        else:
            hpsm_logger.error('Фрейм с заявками не найден ')
            webdriver.get(HPSM_EXIT_PAGE)
            webdriver.quit()
            #Отправка инфы в чат что не получилось взять заявки
            
        
        hpsm_html = webdriver.page_source
        webdriver.get(HPSM_EXIT_PAGE)
        webdriver.close()
        return hpsm_html

    
    def parse_hpsm_html(self, html_source):
        start_string = 'var listConfig = '
        end_string = 'columns: ['
        raw_tickets = html_source[html_source.index(start_string)+len(start_string)+13:html_source.index(end_string)-8]
        return raw_tickets


    def run(self):
        while True:
            try:
                source = self.get_html_page(webdriver=self.create_webdriver()) 
                print(self.parse_hpsm_html(html_source=source))
                sleep(HPSM_CHECK_INTERVAL_SECONDS)
            except Exception as exc:
                print(exc)
                #отправка уведомления 
 