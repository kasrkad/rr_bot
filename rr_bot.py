#!/bin/python3
from selenium import webdriver
import time
import os
# from bot_config import AUTH
import config
from parser import parse_hpsm

def Get_HPSM_table(url):
   if os.path.exists('html'):
      os.remove('html')
   options = webdriver.ChromeOptions()
   # options.add_argument('--headless')
   driver = webdriver.Chrome(config.PATH_TO_DRIVER)
   driver.get(url)
   driver.find_element_by_id("LoginUsername").send_keys(config.USER_NAME)
   driver.find_element_by_id("LoginPassword").send_keys(config.PASSWORD)
   driver.find_element_by_id("loginBtn").click()
   time.sleep(5)
   while True:
      if os.path.exists('html'):
         os.remove('html')
      driver.get(url)
      
      time.sleep(5)
      driver.switch_to.frame(driver.find_element_by_tag_name('iframe'))
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
