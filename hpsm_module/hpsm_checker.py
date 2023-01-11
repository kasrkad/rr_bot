import sys
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from threading import Thread
sys.path.append('../')
from sqlite_module.sql_lib import get_owner_or_duty_db
from bot_exceptions.hpsm_exeptions import GetHpsmFrameException,GetPageException,HpsmLoginException
from config import HPSM_PASS, HPSM_PAGE, HPSM_CHECK_INTERVAL_SECONDS, HPSM_USER, TG_BOT_TOKEN, RR_LIST

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

    def __init__(self,bot_token:str,*args,**kwargs):
        super().__init__(*args, **kwargs)
        self.bot_token = bot_token


    def create_webdriver(self):
        options = webdriver.FirefoxOptions()
        options.add_argument('--headless')
        driver = webdriver.Firefox(executable_path='./geckodriver', options=options)
        driver.set_window_size(1920, 1080)
        return driver


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
        try:
            wait = WebDriverWait(webdriver, 80).until(EC.presence_of_element_located(By.TAG_NAME,"iframe"))
        except Exception as exc:
            print("time out")
            return


        try:
            webdriver.switch_to.frame(webdriver.find_element_by_tag_name('iframe'))
            hpsm_html = webdriver.page_source
        except Exception as exc:
            webdriver.quit()
            hpsm_logger.error('Произошла ошибка при выборе фрейма с заявками.')
            raise GetHpsmFrameException
        
        return hpsm_html

    
    def parse_hpsm_html(self, html_source):
        start_string = 'var listConfig = '
        end_string = 'columns: ['
        raw_tickets = html_source[html_source.index(start_string)+len(start_string)+13:html_source.index(end_string)-8]
        return raw_tickets


    def run(self):
        source = self.get_html_page(webdriver=self.create_webdriver())
        print(self.parse_hpsm_html(html_source=source))



if __name__ == '__main__':
    try:
        checker = Hpsm_checker('token')
        checker.run()
    except Exception as exc:
        print(exc)