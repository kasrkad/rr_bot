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
   options.add_argument('--headless')
   driver = webdriver.Chrome(config.PATH_TO_DRIVER, options=options)
   driver.get(url)
   driver.find_element_by_id("LoginUsername").send_keys(config.USER_NAME)
   driver.find_element_by_id("LoginPassword").send_keys(config.PASSWORD)
   driver.find_element_by_id("loginBtn").click()
   time.sleep(5)
   driver.switch_to.frame(driver.find_element_by_tag_name('iframe'))

   with open ('html', 'w') as f:
      f.write(driver.page_source)
      
   driver.Quit()

if __name__ == '__main__':
   Get_HPSM_table(config.url)
   parse_hpsm('html')
