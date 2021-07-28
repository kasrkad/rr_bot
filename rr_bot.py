from selenium import webdriver
import time
import telebot
import json
import datetime
from config import *

class HpsmChecker:
    """
    Класс для проверки и отсылки в канал ЕСС уведомлений о не взятых в работу заявках в HPSM
    """
    

    def __init__(self, user_login=None, user_password=None, bot_token=None, cycle_check_time=600, group_id='1739060486'):
        self.user_login = user_login
        self.user_password = user_password
        self.hpsm_url = 'https://hpsm.emias.mos.ru/sm/index.do'
        self.cycle_check_time = cycle_check_time
        self.tickets = {}    
        self.group_id = group_id 
        self.rr_tickets_count = 0
        self.duty_engeneer = {}
        self.last_tickets_check = ''
        self.bot = telebot.TeleBot(bot_token, parse_mode='MARKDOWN')
        self.morning_notification = False
        self.evening_notification = False
        self.rr_list = ['Анализ вышедших обновлений и предлагаемых изменений СПО, формирование предложений Заказчику по их внесению в Систему',
                        'Анализ, архивация лог-файлов ППО',
                        'Анализ, архивация лог-файлов СПО',
                        'Контроль создания резервной копии',
                        'Контроль сроков действия лицензий и сертификатов',
                        'Контрольное восстановление Системы из РК и проверка работоспособности Системы после восстановления',
                        'Мониторинг количества документов и дискового пространства, занимаемого индексами Better EHR Server',
                        'Оптимизация индексов под текущее наполнение баз данных',
                        'Перемещение из рабочих баз в архив устаревших версий элементов справочников, классификаторов и протоколов взаимодействия',
                        'Проведение горизонтального и вертикального масштабирования имеющихся решений',
                        'Проверка актуальности информации в СМКСС',
                        'Проверка доступности компонентов Системы',
                        'Проверка прав и атрибутов доступа к Системе',
                        'Проверка срабатывания и уведомлений систем мониторинга, а также анализ необходимости и целесообразности изменения параметров мониторинга Системы',
                        'Своевременный сбор статистики по изменяющимся таблицам баз данных',
                        'Управление объёмом и размещением табличных пространств БД, своевременное определение необходимости расширения и подготовка запроса для расширения выделенного пространства под хранение данных',
                        'Формирование отчетов о произошедших событиях']

    def load_duty_engeneer(self):
        """
        Проверка текущего дежурного
        """
        with open('duty.json', 'r', encoding='utf-8') as duty_line:
            self.duty_engeneer = json.loads(duty_line.read())


    def get_tickets(self):
        """
        Get tickets from hpsm, and write it in hpsm_html_source
        """ 
        options = webdriver.FirefoxOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        driver = webdriver.Firefox(executable_path='./geckodriver',options=options)
        driver.get(self.hpsm_url)
        driver.find_element_by_id("LoginUsername").send_keys(self.user_login)
        driver.find_element_by_id("LoginPassword").send_keys(self.user_password)
        driver.find_element_by_id("loginBtn").click()
        time.sleep(3)
        driver.switch_to.frame(driver.find_element_by_tag_name('iframe'))
        hpsm_html_source = driver.page_source 
        driver.get('https://hpsm.emias.mos.ru/sm/goodbye.jsp?lang=')
        driver.quit()
        return hpsm_html_source


    def parse_html(self, html_source):
        tickets_for_check = []
        start_string = 'var listConfig = '
        end_string = 'columns: ['
        raw_tickets = html_source[html_source.index(start_string)+len(start_string)+13:html_source.index(end_string)-8]
        replace_list = [
        "_{_VALUE_}_request",
        "_{_VALUE_}_4",
        "_{_VALUE_}_AS203",
        "_{_VALUE_}_In work",
        "_{_VALUE_}_AS346",
        "_{_VALUE_}_Assigned",
        "_{_VALUE_}_Planning",
        "_{_VALUE_}_cm3r",
        "_{_VALUE_}_Approval",
        "_{_VALUE_}_cm3t",
        "_{_VALUE_}_Запланировано",
        "_{_VALUE_}_Assigneed",
        "_{_VALUE_}_Выполняется"]

        for replace in replace_list:
            raw_tickets = raw_tickets.replace(replace,"")
        data_dict = json.loads(raw_tickets)
        data_dict = data_dict["model"]["instance"]
        for row in data_dict:
            if row["record_id"].startswith("RF") or row["record_id"].startswith("IM"):
                tickets_for_check.append({"record_id":row["record_id"], "description":row["description"].strip(), "status": row["status"], "group":row["group"], "itemType": row["itemType"],
                "assignee": row["assignee"], "priotity": row["priority"], "sla": row["em_next_ola_breach"]})
        return tickets_for_check    


    def check_working_time(self):
        work_hours = datetime.datetime.now()
        hours = int(work_hours.strftime("%H"))
        minutes = int(work_hours.strftime("%M"))
        self.last_tickets_check = f'{hours:02d}:{minutes:02d}'
        if hours >= 10 and hours < 22:
            return True
        return False

   
    def send_notification(self, ticket_id):
        self.bot.send_message(self.group_id, f"""Заявка [{ticket_id}](https://hpsm.emias.mos.ru/sm/index.do?lang=) не взята в работу!Вызываем ответственных:
[{self.duty_engeneer['first_name']} {self.duty_engeneer['last_name']}](tg://user?id={self.duty_engeneer['t_id']})
{DUTY_OWNER}""")
        self.bot.send_message(self.duty_engeneer['t_id'], f"Заявка [{ticket_id}](https://hpsm.emias.mos.ru/sm/index.do?lang=) не взята в работу!")

    
    def check_sla(self):
        rr_counter = 0
        ticket_counter = 0
        for ticket in self.tickets:
            if ticket['status'] != 'В работе' and self.check_working_time():
               self.send_notification(ticket["record_id"])
            elif ticket['description'] in self.rr_list:
                rr_counter+=1
            ticket_counter+=1
        self.rr_tickets_count = rr_counter
        with open('last_check.json', 'w', encoding='utf8') as json_file:
            json.dump({"check_time":self.last_tickets_check,"tickets_count":ticket_counter}, json_file, ensure_ascii=False)
        self.rr_tickets_count = 0


    def rr_time(self):
        current_hour = datetime.datetime.now().strftime("%H")
        current_min = datetime.datetime.now().strftime("%M")
        week_day = datetime.datetime.today().weekday()
        if week_day != 6:
            if int(current_hour) == 10 and int(current_min) < 11 and self.morning_notification == False :
                self.bot.send_message(self.group_id, f"[{self.duty_engeneer['first_name']} {self.duty_engeneer['last_name']}](tg://user?id={self.duty_engeneer['t_id']}) Время брать РРки!")
                self.morning_notification = True
                self.evening_notification = False
            elif int(current_hour) == 17 and int(current_min) < 11 and self.evening_notification == False:
                self.bot.send_message(self.group_id, f"Эй! [{self.duty_engeneer['first_name']} {self.duty_engeneer['last_name']}](tg://user?id={self.duty_engeneer['t_id']}) Время выполнять РР!")
                self.morning_notification = False
                self.evening_notification = True
            
            if int(current_hour) == 17 and int(current_min) > 30 and self.rr_tickets_count != 0:
                self.bot.send_message(self.group_id,f"Внимание кол-во не закрытых РР - {self.rr_tickets_count}!")
        else:
            if int(current_hour) == 10 and self.morning_notification == False :
                self.bot.send_message(self.group_id, f"Сегодня воскресенье, РР нет.")
                self.morning_notification = True
                self.evening_notification = False
            elif int(current_hour) == 17 and self.evening_notification == False:
                self.bot.send_message(self.group_id, f"Эй! [{self.duty_engeneer['first_name']} {self.duty_engeneer['last_name']}](tg://user?id={self.duty_engeneer['t_id']}) Сегодня не делаешь РР, возрадуйся!")
                self.morning_notification = False
                self.evening_notification = True


    def run(self):
        try:
            while True:
                if self.check_working_time():
                    self.load_duty_engeneer()
                    html = self.get_tickets()
                    self.tickets = self.parse_html(html)
                    self.check_sla()
                    print(self.rr_tickets_count)
                    self.rr_time()
                    time.sleep(int(self.cycle_check_time))
                else:
                    time.sleep(600)
        except Exception as e:
            self.bot.send_message(ECC_CHAT_ID, f"Я сломался {e.args}")
            print(e)


if __name__ == '__main__':

    checker = HpsmChecker(user_login = HPSM_USER, user_password = HPSM_PASS, bot_token = TG_BOT_TOKEN, cycle_check_time = HPSM_CHECK_INTERVAL_SECONDS, group_id = ECC_CHAT_ID)
    checker.run()
