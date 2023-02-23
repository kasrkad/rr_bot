from json import loads
from time import sleep
from threading import Thread
from datetime import datetime
import telebot
from selenium import webdriver
from ..logger_config.logger_data import create_logger
from ..sqlite_module.sql_lib import get_owner_or_duty_db, write_hpsm_status_db
from ..bot_exceptions.hpsm_exceptions import *
from .hpsm_config import *


# configure logger
hpsm_logger = create_logger(__name__)


class Hpsm_checker(Thread):

    def __init__(self, bot_token: str, rr_file_path: str, request_codes_file_path: str, control_queue, *args, **kwargs) -> None:
        """Класс парсера HPSM для мониторинга состояния заявок и уведомлении о необходимости взять в работу

        Args:
            bot_token (str): строка с токеном телеграм бота
            rr_file_path (str): файл с описанием Регламентных работ
            request_codes_file_path (str): файл с описание кодов регламентных работ
            control_queue (queue): очередь для взаимодействия с инстансом service bot 
        """
        super().__init__(*args, **kwargs)
        self.bot_token = bot_token
        self.rr_file_path = rr_file_path
        self.control_queue = control_queue
        self.request_codes_file_path = request_codes_file_path
        self.rr_list = []
        self.send_notifi_flag = True
        self.request_codes = []
        self.count_failed_checks = 0

    def create_bot(self):
        """Возвращаем объект бота для работы с уведомлениями о заявках

        Returns:
            _type_: _description_
        """
        bot = telebot.TeleBot(self.bot_token, parse_mode='MARKDOWN')
        return bot

    def start_control_queue(self):
        """Мониторинг очереди взаимодействия с инстанса сервисобота
        """
        hpsm_logger.info('Запускаем очередь управления hpsm мониторинга.')
        while True:
            try:
                data = self.control_queue.get()
                hpsm_logger.info(f'получено сообщение в очередь {data}')
                if data is None:
                    break
                if data[1] == 'notification_status':
                    hpsm_logger.info(
                        "Запрошен статус уведомлений от HPSM CHECKER")
                    self.send_notification(
                        text=f"Статус уведомлений от HPSM_CHECKER {self.send_notifi_flag}", channel=True)
                if data[1] == 'notification_off':
                    hpsm_logger.info('Уведомления HPSM отключены от {data[0]}')
                    self.send_notification(
                        text='Уведомления о заявках отключены.', channel=True)
                    self.send_notifi_flag = False
                if data[1] == 'notification_on':
                    hpsm_logger.info('Уведомления HPSM включены от {data[0]}')
                    self.send_notifi_flag = True
                    self.send_notification(
                        text='Уведомления о заявках включены', channel=True)
                if data[1] == 'screenshot':
                    hpsm_logger.info(
                        'В очереди пришла команда на снятие скриншота')
                    self.make_screenshot()
                    self.send_notification(
                        text='Проверьте скриншот, для отправки нажмите на /send', screenshot=True)
                else:
                    print(f'неизвестный параметр {data[1]} от {data[0]}')
            except Exception:
                hpsm_logger.error(
                    'Ошибка при работе с очередью command = {data}')

    def send_notification(self, text: str, channel=False, duty=False, owner=False, screenshot=False):
        """Отправка уведомления

        Args:
            text (str): Текст для отправки
            channel (bool, optional): Отправить уведомление в канал ЕСС,линкануть дежурного и координатора. Defaults to False.
            duty (bool, optional): Отправить только дежурному. Defaults to False.
            owner (bool, optional): Отправить только координатору. Defaults to False.
            screenshot (bool, optional): Отправить скриншот дежурному. Defaults to False.
        """
        hpsm_logger.info('Отправляем уведомление')
        notifi_bot = self.create_bot()
        duty_now = get_owner_or_duty_db(role='duty')
        owner_now = get_owner_or_duty_db(role='owner')
        keyboard = None
        try:
            if screenshot:
                hpsm_logger.info(f'Отправляем скриншот для {str(duty_now)}')
                notifi_bot.send_message(duty_now['tg_id'], text)
                hpsm_logger.info('Сообщение отправлено')
                notifi_bot.send_photo(duty_now['tg_id'], photo=open(
                    'screenshot_hpsm.jpg', 'rb'))
                hpsm_logger.info('Скриншот отправлен.')
            if channel and self.send_notifi_flag:
                notifi_bot.send_message(
                    ESS_CHAT_ID, text+f"\n[{duty_now['fio']}](tg://user?id={duty_now['tg_id']})\n[{owner_now['fio']}](tg://user?id={owner_now['tg_id']})")
            if duty and self.send_notifi_flag:
                notifi_bot.send_message(
                    duty_now['tg_id'], text, reply_markup=keyboard)
            if owner and self.send_notifi_flag:
                notifi_bot.send_message(owner_now['tg_id'], text)
        except Exception:
            hpsm_logger.error(
                "Произошла ошибка при отправке уведомления", exc_info=True)

    def make_screenshot(self):
        """Снятие скриншота со страницы с заявками

        Raises:
            HpsmScreenshotError: Произошла ошибка при снятии скриншота
        """
        driver = self.create_webdriver()
        driver.get(HPSM_PAGE)
        self.login_hpsm(driver, user=HPSM_SCREENSHOT_USER,
                        password=HPSM_SCREENSHOT_PASSWORD)
        self.wait_for_frame(driver, HPSM_WAIT_FRAME_TRIES)
        try:
            driver.get_screenshot_as_file("screenshot_hpsm.jpg")
            driver.get('https://hpsm.emias.mos.ru/sm/goodbye.jsp?lang=')
            driver.quit()
        except Exception:
            hpsm_logger.error(
                'Произошла ошибка при получении скриншота.', exc_info=True)
            raise HpsmScreenshotError

    def check_tickets_for_notification(self, tickets: dict):
        """Проверяем заявки на статус , если не в ignore_statuses, и проходит по условями, то отправить уведомление в канал 
        """
        hpsm_logger.info('проверяем заявки на необходимость уведомления')
        current_hour = datetime.now().strftime("%H")
        current_min = datetime.now().strftime("%M")
        ignore_statuses = ['В работе', 'Отложен',
                           'Ожидание', 'Подготовка Отчета']
        message_for_get_request = """Заявка [{ticket_id}](https://hpsm.emias.mos.ru/sm/index.do?lang=) не взята в работу!"""
        message_with_rr_count = """В работе осталось {rr_count} не закрытых РР!"""
        hpsm_logger.info(
            f'Проверяем заявки на соответствие времени уведомлений {current_hour} : {current_min}.')

        for ticket in tickets:
            if self.check_working_time() and ticket['status'] not in ignore_statuses and not(ticket['record_id'].startswith('C') or ticket['record_id'].startswith('T')):
                hpsm_logger.info(
                    f'Отправляем уведомление по заявке {ticket["record_id"]}')
                self.send_notification(text=message_for_get_request.format(ticket_id=ticket['record_id']), channel=True,
                                       owner=True, duty=True)
        rr_counter = self.get_rr_count(tickets=tickets)['rr_task_count']
        hpsm_logger.info(f'Кол-во РР = {rr_counter} сработка условий - ' + str(int(
            current_hour) == 17 and int(current_min) > 30 and rr_counter != 0 and self.check_working_time()))

        if (int(current_hour) == 17 and int(current_min) > 30) and rr_counter != 0 and self.check_working_time():
            hpsm_logger.warning(
                f'Отправляем уведомление по открытым РР {rr_counter}')
            self.send_notification(text=message_with_rr_count.format(
                rr_count=rr_counter), channel=True)

    def create_webdriver(self):
        """Создаем объект драйвера для работы с сайтом заявок

        Returns:
        объект драйвера
        """
        hpsm_logger.info('Создаем драйвер')
        options = webdriver.FirefoxOptions()
        options.add_argument('--headless')
        driver = webdriver.Firefox(
            executable_path='./geckodriver', options=options)
        driver.set_window_size(1920, 1080)
        return driver

    def check_working_time(self):
        """Проверка на рабочее время 

        Returns:
           True: если текущее время - рабочее
           False: если время не рабочее 
        """
        work_hours = datetime.now()
        hours = int(work_hours.strftime("%H"))
        week_day = datetime.today().weekday()
        if hours >= 10 and hours < 22 and week_day != 6:
            return True
        return False

# TODO объеденить функции загрузки из файлов с РР
    def load_request_codes_from_file(self):
        with open(self.request_codes_file_path, 'r', encoding='utf8') as request_code_file:
            for line in request_code_file:
                self.request_codes.append(line.strip())

    def load_rr_from_file(self):
        with open(self.rr_file_path, 'r', encoding='utf8') as rr_file:
            for line in rr_file:
                self.rr_list.append(line.strip())

    def wait_for_frame(self, webdriver, timeout: int):
        """Ожидание загрузки элемента страницы с заявками

        Args:
            webdriver (obj): Объект драйвера для работы с сайтом
            timeout (int): кол-во попыток для поиска элемента с заявками (секунды)

        Raises:
            GetHpsmFrameException: _description_
        """
        try_counter = 1
        hpsm_logger.info('Делаем паузу для загрузки страницы')
        while try_counter < timeout:

            try:
                webdriver.switch_to.frame(
                    webdriver.find_element_by_tag_name('iframe'))
            except KeyboardInterrupt:
                hpsm_logger.error('Операция прервана пользователем')
                webdriver.get(HPSM_EXIT_PAGE)
                webdriver.close()
            except Exception:
                hpsm_logger.info(
                    f"Элемент iframe не обнаружен попытка №{try_counter}")
                sleep(1)
                try_counter += 1
                continue
            else:
                sleep(10)
                hpsm_logger.info(
                    f'Количество попыток для получения списка заявок - {try_counter}')
                break
        else:
            hpsm_logger.error('Фрейм с заявками не найден')
            webdriver.get(HPSM_EXIT_PAGE)
            webdriver.quit()
            raise GetHpsmFrameException

    def login_hpsm(self, webdriver, user: str, password: str):
        """Логинимся в HPSM

        Args:
            webdriver (obj): 
            user (str): пользователь для логина 
            password (str): пароль для пользователя

        Raises:
            HpsmLoginException: Если не получилось залогиниться

        Returns:
            Вернуть драйвер с залогиненым сайтом            
        """
        hpsm_logger.info('Логинимся с учеткой - ' + user)
        try:
            hpsm_logger.info(
                'Добавляем cookie на кол-во строк в странице = 50')
            webdriver.add_cookie({'name': 'pagesize', 'value': '50'})
            webdriver.find_element_by_id('LoginUsername').send_keys(user)
            webdriver.find_element_by_id('LoginPassword').send_keys(password)
            webdriver.find_element_by_id('loginBtn').click()
            return webdriver
        except Exception as exc:
            webdriver.quit()
            hpsm_logger.error(
                f'Произошла ошибка при логине с учетными данными {user}', exc_info=True)
            print(exc.args)
            raise HpsmLoginException

    def get_html_page(self, webdriver) -> str:
        """Парсим страницу с заявками

        Args:
            webdriver (obj): Вебдрайвер селениума с открытой страницей 

        Raises:
            GetPageException: Исключение при получении html страницы

        Returns:
            str: html код страницы с заявками
        """
        hpsm_logger.info(f'Запрашиваем страницу {HPSM_PAGE}')

        try:
            webdriver.get(HPSM_PAGE)
        except Exception:
            webdriver.quit()
            hpsm_logger.error(
                f'Произошла ошибка в запросе страницы {HPSM_PAGE}', exc_info=True)
            raise GetPageException

        webdriver_login = self.login_hpsm(
            webdriver, user=HPSM_USER, password=HPSM_PASS)
        self.wait_for_frame(webdriver_login, 80)
        hpsm_html = webdriver_login.page_source
        webdriver.get(HPSM_EXIT_PAGE)
        webdriver.close()
        hpsm_logger.info('Драйвер и соединение закрыто.')
        return hpsm_html

    def parse_hpsm_html(self, html_source: str) -> list:
        """Вытаскиваем заявки из общего кода страницы

        Args:
            html_source (str): html строка с кодом страницы с заявками

        Raises:
            EmptyRequestsListReturn: исключение если заявки не найдены

        Returns:
            list: список с dict объектами заявок
        """
        start_string = 'var listConfig = '
        end_string = 'columns: ['
        tickets_keys = ['record_id', 'itemType',
                        'description', 'status', 'group', 'priority']
        ready_tickets = []
        raw_tickets = html_source[html_source.index(
            start_string)+len(start_string)+13:html_source.index(end_string)-8]

        for replace_elem in self.request_codes:
            raw_tickets = raw_tickets.replace(replace_elem, "")
        data_tickets = loads(raw_tickets)['model']['instance']

        for ticket in data_tickets:
            new_ticket = {}
            for key, value in ticket.items():
                if key in tickets_keys:
                    if key == 'priority':
                        value = value.split(" ")[0]
                    new_ticket[key] = value
            ready_tickets.append(new_ticket)

        if ready_tickets:
            return ready_tickets
        raise EmptyRequestsListReturn('Вернулся пустой список заявок')

    def get_rr_count(self, tickets: list) -> dict:
        """Считаем кол-во регламентных работ, и обычных заявок

        Args:
            tickets (list): Список с заявками 

        Returns:
            dict: кол-во заявок и рр для базы данных 
        """
        rr_counter = 0
        for ticket in tickets:
            if ticket['description'] in self.rr_list:
                rr_counter += 1
        return {'rr_task_count': rr_counter, 'task_count': (len(tickets)-rr_counter)}

    def run(self):
        try:
            hpsm_logger.info('Создаем ,запускаем очередь.')
            queue = Thread(target=self.start_control_queue)
            queue.start()
        except Exception as exc:
            hpsm_logger.critical("Очередь не запущена!", exc_info=True)
            print(exc, exc.args)
        while True:
            try:
                self.load_rr_from_file()
                self.load_request_codes_from_file()
                source = self.get_html_page(webdriver=self.create_webdriver())
                tickets = self.parse_hpsm_html(source)
                self.check_tickets_for_notification(tickets=tickets)
                hpsm_logger.info('Записываем данные о заявках из HPSM в БД')
                write_hpsm_status_db(**self.get_rr_count(tickets))
                self.count_failed_checks = 0
            except GetHpsmFrameException as exc:
                hpsm_logger.error(
                    'Произошла ошибка при получении заявок с HPSM.')
                self.count_failed_checks += 1
                if self.count_failed_checks >= 2 and self.check_working_time():
                    self.send_notification(
                        text=f'Ошибка при получении заявок с HPSM следующая попытка через {HPSM_CHECK_INTERVAL_SECONDS} секунд.', channel=True)
            except EmptyRequestsListReturn as exc:
                hpsm_logger.warning('Вернулся пустой список задач с HPSM.')
                write_hpsm_status_db()
                print(exc, exc.args)
            except HpsmScreenshotError as exc:
                self.send_notification(
                    'Ошибка в получении скриншота HPSM, необходимо сделать скриншот в ручную.')
            except Exception as exc:
                print(exc, exc.args)
                hpsm_logger.error(
                    'Возникло необрабатываемое исключение', exc_info=True)
                self.count_failed_checks += 1
                if self.count_failed_checks >= 2 and self.check_working_time():
                    self.send_notification(
                        text=f'Ошибка при получении заявок с HPSM следующая попытка через {HPSM_CHECK_INTERVAL_SECONDS} секунд.', channel=True)
            finally:
                sleep(HPSM_CHECK_INTERVAL_SECONDS)
