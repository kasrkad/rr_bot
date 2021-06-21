#!/bin/python3
from os import write
from selenium import webdriver
import time
import config
from parser import parse_hpsm
import telebot
import json

def check_sla(filename):
   rr_bot = telebot.TeleBot(config.BOT_TOKEN, parse_mode='MARKDOWN')
   with open (filename, 'r') as rr_file:
	   for line in rr_file.readlines():
	   	line = line.replace("'",'"')
	   	rr = json.loads(line)
	   	if rr['status'] != 'В работе':
	   		print(rr_bot.send_message(config.CHAT_ID, f"Заявка [{rr['record_id']}](https://hpsm.emias.mos.ru/sm/index.do?lang=) не взята в работу! Вызываем ответственных [Алесандра Баумана](tg://user?id=753785354) и Дежурный"))
	   		print(rr_bot.send_message('1739060486', f"Заявка [{rr['record_id']}](https://hpsm.emias.mos.ru/sm/index.do?lang=) не взята в работу!" ))

def Get_HPSM_table(url):
   with open ('work_log', 'a') as log:
      log.write("Установка опций\n")
      options = webdriver.FirefoxOptions()
      options.add_argument('--headless')
      options.add_argument('--no-sandbox')
      log.write('Запускаем драйвер\n')
      driver = webdriver.Firefox(executable_path=config.GECKOPASS,options=options)
      
      log.write("Открываем сайт\n")
      driver.get(url)
      log.write("Передаем данные для логина\n")
      driver.find_element_by_id("LoginUsername").send_keys(config.USER_NAME)
      driver.find_element_by_id("LoginPassword").send_keys(config.PASSWORD)
      log.write("Кликаем на логин\n")
      driver.find_element_by_id("loginBtn").click()
      log.write("Загружаем страницу\n")
      time.sleep(3)
      log.write('Переходим на таблицу\n')
      driver.switch_to.frame(driver.find_element_by_tag_name('iframe'))
      
      log.write('Дампим таблицу\n')
      with open ('html', 'w') as f:
            f.write(driver.page_source)

      log.write('Разлогиниваемся\n')
      driver.get('https://hpsm.emias.mos.ru/sm/goodbye.jsp?lang=')
      log.write('Закрываем драйвер\n')
      driver.quit()

if __name__ == '__main__':
   while True:
      Get_HPSM_table(config.url)
      parse_hpsm('html')
      check_sla('monitor_actual.json')
      time.sleep(config.CHECK_TIME)

