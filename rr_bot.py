#!/bin/python3
# from os 
from selenium import webdriver
import time
import telebot
import json

from bot_functions import load_from_json, check_working_time
from parser import parse_hpsm
import config

def check_sla(filename):
    """[Проверка не взятых в работу заявок]

    Args:
        filename (file): [принимает на вход json со списоком заявок парсит в словарь, ищет заявки со статусом отличным от "В работе"]
    """
    rr_bot = telebot.TeleBot(config.BOT_TOKEN, parse_mode='MARKDOWN')
    duty = load_from_json('duty.json')
    with open (f"./parse_logs/{filename}", 'r') as rr_file:
        for line in rr_file.readlines():
            line = line.replace("'",'"')
            rr = json.loads(line)
            if rr['status'] != 'В работе' and check_working_time():
                rr_bot.send_message(config.CHAT_ID, f"Заявка [{rr['record_id']}](https://hpsm.emias.mos.ru/sm/index.do?lang=) не взята в работу!Вызываем ответственных: \n {config.DUTY_OWNER} \n [{duty['first_name']} {duty['last_name']}](tg://user?id={duty['t_id']})")
                rr_bot.send_message(duty['t_id'], f"Заявка [{rr['record_id']}](https://hpsm.emias.mos.ru/sm/index.do?lang=) не взята в работу!")

def Get_HPSM_table(url):
    """[Дампит таблицу с заявками с hpsm]

    Args:
        url (url-string): [Парсит сайт, дампит результат выполнения js-скрипта формирующего таблицу, разлогинивается с сайта после дампа]
    """
    options = webdriver.FirefoxOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    driver = webdriver.Firefox(executable_path=config.GECKOPASS,options=options)
    
    driver.get(url)
    driver.find_element_by_id("LoginUsername").send_keys(config.USER_NAME)
    driver.find_element_by_id("LoginPassword").send_keys(config.PASSWORD)
    driver.find_element_by_id("loginBtn").click()
    time.sleep(3)
    driver.switch_to.frame(driver.find_element_by_tag_name('iframe'))
    
    with open ('html', 'w') as f:
          f.write(driver.page_source)

    driver.get('https://hpsm.emias.mos.ru/sm/goodbye.jsp?lang=')
    driver.quit()

if __name__ == '__main__':
    try:
        while True:
            if check_working_time():
                Get_HPSM_table(config.url)
                parse_hpsm('html')
                check_sla('monitor_actual.json')
                time.sleep(config.CHECK_TIME)
            else:
                time.sleep(1800)
                continue
    except Exception as exc:
        print (exc)
        with open('exc_parse.txt', 'a', encoding='utf8') as exc_file:
            exc_file.write(str(exc))
        pass
