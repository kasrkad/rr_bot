#!/bin/python3
from selenium import webdriver
import time
# from bot_config import AUTH
import config
from parser import parse_hpsm

def Get_HPSM_table(url):
   print("Установка опций")
   options = webdriver.FirefoxOptions()
   options.add_argument('--headless')
   options.add_argument('--no-sandbox')
   print('Запускаем драйвер')
   driver = webdriver.Firefox(executable_path=config.GECKOPASS,options=options)
   print ("Открываем сайт")
   driver.get(url)
   print ("Передаем данные для логина")
   driver.find_element_by_id("LoginUsername").send_keys(config.USER_NAME)
   driver.find_element_by_id("LoginPassword").send_keys(config.PASSWORD)
   print("Кликаем на логин")
   driver.find_element_by_id("loginBtn").click()
   print("Загружаем страницу")
   time.sleep(3)
   print('Переходим на таблицу')
   driver.switch_to.frame(driver.find_element_by_tag_name('iframe'))
   print ('Дампим таблицу')
   with open ('html', 'w') as f:
         f.write(driver.page_source)
   print('Разлогиниваемся')
   driver.get('https://hpsm.emias.mos.ru/sm/goodbye.jsp?lang=')
   print('Закрываем драйвер')
   driver.quit()

if __name__ == '__main__':
   while True:
      Get_HPSM_table(config.url)
      print ('Парсим таблицу')
      parse_hpsm('html')
      print(f"Пауза перед след запуском {config.CHECK_TIME} секунд")
      time.sleep(config.CHECK_TIME)

