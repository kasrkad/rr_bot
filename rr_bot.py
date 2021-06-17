#!/bin/python3
from selenium import webdriver
import time
import os
# from bot_config import AUTH
import config
from parser import parse_hpsm

def Get_HPSM_table(url):
   print("установка опций")
   options = webdriver.FirefoxOptions()
   options.add_argument('--headless')
   options.add_argument('--no-sandbox')
   print('Запускаем драйвер')
   driver = webdriver.Firefox(executable_path=r'/path/to/geckodriver',options=options)
   print ("дергаем сайт")
   driver.get(url)
   print ("передаем лог пасс")
   driver.find_element_by_id("LoginUsername").send_keys(config.USER_NAME)
   driver.find_element_by_id("LoginPassword").send_keys(config.PASSWORD)
   print("кликаем на логин")
   driver.find_element_by_id("loginBtn").click()
   print("pause")
   time.sleep(5)
   while True:
      if os.path.exists('html'):
         os.remove('html')
      print("обновляем страницу")
      # driver.get(url)

      
      time.sleep(5)
      print("переходим на элемент")
      driver.switch_to.frame(driver.find_element_by_tag_name('iframe'))
      print ("pause")
      time.sleep(2)
      with open ('html', 'w') as f:
         f.write(driver.page_source)
      driver.switch_to.default_content()
      time.sleep(5)
      driver.get('https://hpsm.emias.mos.ru/sm/goodbye.jsp?lang=')
      time.sleep(3)
      parse_hpsm('html')
      driver.get(url)
      driver.find_element_by_id("LoginUsername").send_keys(config.USER_NAME)
      driver.find_element_by_id("LoginPassword").send_keys(config.PASSWORD)
      driver.find_element_by_id("loginBtn").click()


if __name__ == '__main__':
   Get_HPSM_table(config.url)
