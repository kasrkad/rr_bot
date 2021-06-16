#!/bin/python3
import requests
from selenium import webdriver
from bs4 import BeautifulSoup
import time
# from bot_config import AUTH
# import bot_config
url = 'https://hpsm.emias.mos.ru/sm/index.do'
driver = webdriver.Chrome('path_to_chrome_driver')
driver.get(url)
driver.find_element_by_id("LoginUsername").send_keys("username")
driver.find_element_by_id("LoginPassword").send_keys("password")
driver.find_element_by_id("loginBtn").click()
time.sleep(5)
driver.switch_to.frame(driver.find_element_by_tag_name('iframe'))

with open ('html', 'w') as f:
   f.write(driver.page_source)




