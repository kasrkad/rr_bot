#!/bin/python3
import requests
from requests.models import HTTPBasicAuth
from requests.sessions import session
from bs4 import BeautifulSoup
# from bot_config import AUTH
import time
# import bot_config

rr_page = 'https://hpsm.emias.mos.ru/sm/index.do?lang=ru'
session  = requests.Session()

authorization = session.post('https://hpsm.emias.mos.ru/sm/index.do?lang=', data={
	'user.id': 'MeleshenkovI',
	'xHtoken': None,
	'old.password': 'Boradori4040',
	 'L.language': 'ru',
	 'type':'login',
	'originalUrl':'https://hpsm.emias.mos.ru/sm/index.do?lang=ru',
	} )
print(authorization)
some_headers = dict(authorization.headers)
one, two, three, four, five, six = some_headers['set-cookie'].split(";")

print (one[11:])

head = {  'Cookie': f'JSESSIONID={one[11:]}; mode=index.do; lang=ru',
    'lang':'ru',
    'mode':"index.do",
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0',
    'Host':'hpsm.emias.mos.ru',
    'Connection':'keep-alive',
    'Referer': 'https://hpsm.emias.mos.ru/sm/index.do'
}
print(head)

rr = session.get(rr_page, headers = head )

print (rr.text)


# rr = session.get(rr_page)
# print(session.cookies)

# rr = session.get(rr_page, auth= HTTPBasicAuth('MeleshenkovI', 'Boradori4040'))
# print(rr)
# print (rr.text)
# html = BeautifulSoup(rr.text, features='html.parser')
