#!/bin/python3
import requests
from requests.models import HTTPBasicAuth
from requests.sessions import session
from bs4 import BeautifulSoup
from bot_config import AUTH
import time
import bot_config

rr_page = 'https://hpsm.emias.mos.ru/sm/index.do?lang='
session  = requests.Session()

authorization = session.post('https://hpsm.emias.mos.ru/sm/index.do?lang=', {
	'user.id': 'MeleshenkovI',
	'xHtoken': None,
	'old.password': 'Boradori4040',
	'L.language': 'ru',
	'type':'login',
	'originalUrl':'https://hpsm.emias.mos.ru/sm/index.do?lang=ru',
	} )


rr = session.get(rr_page, headers=authorization.headers)

print (rr.text)


# rr = session.get(rr_page)
# print(session.cookies)

# rr = session.get(rr_page, auth= HTTPBasicAuth('MeleshenkovI', 'Boradori4040'))
# print(rr)
# print (rr.text)
# html = BeautifulSoup(rr.text, features='html.parser')