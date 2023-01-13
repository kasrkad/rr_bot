#!/bin/python3
from os import environ
DEV_SOAP_URL = environ['DEV_SOAP_URL']
#Настройки для пересоздания ЕСУ_Продюсера
PRODUCER_SOAP_USER = environ['PRODUCER_SOAP_USER']
PRODUCER_SOAP_PASS = environ['PRODUCER_SOAP_PASS']
SIMI_DNS_NAME_ENDPOINT_TEMPLATE = environ['SIMI_DNS_NAME_ENDPOINT_TEMPLATE']
SIMIP3_DNS_NAME_ENDPOINT_TEMPLATE = environ['SIMIP3_DNS_NAME_ENDPOINT_TEMPLATE']
DEV_ORACLE_CONNECTION_STRING = environ['DEV_DOC_CONNECTION_STRING']
PPAK_STANDBY_ORACLE_CONNECTION_STRING = environ['PPAK_STANDBY_CONNECTION_STRING']


#Настройки доступа до Репозитория ССТ
SIMI_DOC_REPO_FOLDER = environ['SIMI_DOC_REPO_FOLDER']
SIMI_DOC_REPO_USER = environ['SIMI_DOC_REPO_USER']
SIMI_DOC_REPO_PASS = environ['SIMI_DOC_REPO_PASS']
SIMI_DOC_REPO_URL = environ['SIMI_DOC_REPO_URL']

#Настройки бота
ESS_CHAT_ID = environ['ESS_CHAT_ID']
TEST_STAND_GROUP_ID = environ['TEST_STAND_GROUP_ID']
MPAK_GROUP_ID = environ['MPAK_GROUP_ID']
TG_BOT_TOKEN = environ['TG_BOT_TOKEN']
#Настройки скачивания документов
PPAK_SOAP_URL = environ['PPAK_SOAP_URL']
PPAK_SOAP_USER = environ['PPAK_SOAP_USER']
#Настройки доступа до астериска для смены номера
ASTERISK_LOGIN = environ['ASTERISK_LOGIN']
ASTERISK_PASS = environ['ASTERISK_PASS']
#Настройки стендов для работы с ССТ
DEFAULT_ORACLE_USER = environ['DEFAULT_ORACLE_USER']
DEFAULT_ORACLE_PASS = environ['DEFAULT_ORACLE_PASS']
DEFAULT_MARAND_USER = environ['DEFAULT_MARAND_USER']
DEFAULT_MARAND_PASS = environ['DEFAULT_MARAND_PASS']
READ_MARAND_USER = environ['READ_MARAND_USER']
READ_MARAND_PASS = environ['READ_MARAND_PASS']
#МПАК
MPAK_DOC_CONNECTION_STRING =environ['MPAK_DOC_CONNECTION_STRING']
MPAK_BE_IP =environ['MPAK_BE_IP']
MPAK_SIMI_IP =environ['MPAK_SIMI_IP']
#ТЕСТ и ТЕСТ чтение
DEV_DOC_CONNECTION_STRING = environ['DEV_DOC_CONNECTION_STRING']
DEV_BE_IP = environ['DEV_BE_IP']
DEV_SIMI_IP = environ['DEV_SIMI_IP']
DEV_READ_DOC_CONNECTION_STRING =environ['DEV_READ_DOC_CONNECTION_STRING']
DEV_READ_BE_IP = environ['DEV_READ_BE_IP']
DEV_READ_SIMI_IP = environ['DEV_READ_SIMI_IP']
#ПРЕДППАК И ПРЕДППАК чтение
PREDPPAK_DOC_CONNECTION_STRING = environ['PREDPPAK_DOC_CONNECTION_STRING']
PREDPPAK_BE_IP = environ['PREDPPAK_BE_IP']
PREDPPAK_SIMI_IP = environ['PREDPPAK_SIMI_IP']
PREDPPAK_READ_DOC_CONNECTION_STRING = environ['PREDPPAK_READ_DOC_CONNECTION_STRING']
PREDPPAK_READ_BE_IP = environ['PREDPPAK_READ_BE_IP']
PREDPPAK_READ_SIMI_IP = environ['PREDPPAK_READ_SIMI_IP']
#Настройки для офисных стендов
#75
BE_IP_75 = environ['BE_IP_75']
ORACLE_75 = environ['ORACLE_75']
SIMI_IP_75 = environ['SIMI_IP_75']
#71
BE_IP_71 = environ['BE_IP_71']
ORACLE_71 = environ['ORACLE_71']
SIMI_IP_71 = environ['SIMI_IP_71']
#73
BE_IP_73 = environ['BE_IP_73']
ORACLE_73 = environ['ORACLE_73']
SIMI_IP_73 = environ['SIMI_IP_73']


#Для валидации строки с артефактами загрузки в ДЕВ
CORRECT_ARTIFACTS = ['cct','vis','tmpl']

#HPSM настройки
HTTP_PROXY = environ['HTTP_PROXY']
HPSM_USER = environ['HPSM_USER']
HPSM_PASS = environ['HPSM_PASS']
HPSM_CHECK_INTERVAL_SECONDS = environ['HPSM_CHECK_INTERVAL_SECONDS']
HPSM_PAGE = 'https://hpsm.emias.mos.ru/sm/index.do'
HPSM_EXIT = 'https://hpsm.emias.mos.ru/sm/goodbye.jsp?lang='


HPSM_REPLACE = [
        "_{_VALUE_}_request",
		"_{_VALUE_}_AS392",
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
        "_{_VALUE_}_Выполняется",
        "_{_VALUE_}_Delayed",
        '_{_VALUE_}_Waiting']