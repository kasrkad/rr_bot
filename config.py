#!/bin/python3
import os

#Настройки для пересоздания ЕСУ_Продюсера
PRODUCER_SOAP_USER = os.environ['PRODUCER_SOAP_USER']
PRODUCER_SOAP_PASS = os.environ['PRODUCER_SOAP_PASS']
SIMI_DNS_NAME_ENDPOINT_TEMPLATE = os.environ['SIMI_DNS_NAME_ENDPOINT_TEMPLATE']
SIMIP3_DNS_NAME_ENDPOINT_TEMPLATE = os.environ['SIMIP3_DNS_NAME_ENDPOINT_TEMPLATE']
DEV_ORACLE_CONNECTION_STRING = os.environ['DEV_DOC_CONNECTION_STRING']
PPAK_STANDBY_ORACLE_CONNECTION_STRING = os.environ['PPAK_STANDBY_CONNECTION_STRING']


#Настройки доступа до Репозитория ССТ
SIMI_DOC_REPO_FOLDER = os.environ['SIMI_DOC_REPO_FOLDER']
SIMI_DOC_REPO_USER = os.environ['SIMI_DOC_REPO_USER']
SIMI_DOC_REPO_PASS = os.environ['SIMI_DOC_REPO_PASS']
SIMI_DOC_REPO_URL = os.environ['SIMI_DOC_REPO_URL']

#HPSM настройки
HTTP_PROXY = os.environ['HTTP_PROXY']
HPSM_USER = os.environ['HPSM_USER']
HPSM_PASS = os.environ['HPSM_PASS']
HPSM_CHECK_INTERVAL_SECONDS = os.environ['HPSM_CHECK_INTERVAL_SECONDS']
#Настройки бота
ESS_CHAT_ID = os.environ['ESS_CHAT_ID']
TEST_STAND_GROUP_ID = os.environ['TEST_STAND_GROUP_ID']
MPAK_GROUP_ID = os.environ['MPAK_GROUP_ID']
TG_BOT_TOKEN = os.environ['TG_BOT_TOKEN']
#Настройки скачивания документов
PPAK_SOAP_URL = os.environ['PPAK_SOAP_URL']
PPAK_SOAP_USER = os.environ['PPAK_SOAP_USER']
#Настройки доступа до астериска для смены номера
ASTERISK_LOGIN = os.environ['ASTERISK_LOGIN']
ASTERISK_PASS = os.environ['ASTERISK_PASS']
#Настройки стендов для работы с ССТ
DEFAULT_ORACLE_USER = os.environ['DEFAULT_ORACLE_USER']
DEFAULT_ORACLE_PASS = os.environ['DEFAULT_ORACLE_PASS']
DEFAULT_MARAND_USER = os.environ['DEFAULT_MARAND_USER']
DEFAULT_MARAND_PASS = os.environ['DEFAULT_MARAND_PASS']
READ_MARAND_USER = os.environ['READ_MARAND_USER']
READ_MARAND_PASS = os.environ['READ_MARAND_PASS']
#МПАК
MPAK_DOC_CONNECTION_STRING =os.environ['MPAK_DOC_CONNECTION_STRING']
MPAK_BE_IP =os.environ['MPAK_BE_IP']
MPAK_SIMI_IP =os.environ['MPAK_SIMI_IP']
#ТЕСТ и ТЕСТ чтение
DEV_DOC_CONNECTION_STRING = os.environ['DEV_DOC_CONNECTION_STRING']
DEV_BE_IP = os.environ['DEV_BE_IP']
DEV_SIMI_IP = os.environ['DEV_SIMI_IP']
DEV_READ_DOC_CONNECTION_STRING =os.environ['DEV_READ_DOC_CONNECTION_STRING']
DEV_READ_BE_IP = os.environ['DEV_READ_BE_IP']
DEV_READ_SIMI_IP = os.environ['DEV_READ_SIMI_IP']
#ПРЕДППАК И ПРЕДППАК чтение
PREDPPAK_DOC_CONNECTION_STRING = os.environ['PREDPPAK_DOC_CONNECTION_STRING']
PREDPPAK_BE_IP = os.environ['PREDPPAK_BE_IP']
PREDPPAK_SIMI_IP = os.environ['PREDPPAK_SIMI_IP']
PREDPPAK_READ_DOC_CONNECTION_STRING = os.environ['PREDPPAK_READ_DOC_CONNECTION_STRING']
PREDPPAK_READ_BE_IP = os.environ['PREDPPAK_READ_BE_IP']
PREDPPAK_READ_SIMI_IP = os.environ['PREDPPAK_READ_SIMI_IP']
#ТПАК
TPAK_DOC_CONNECTION_STRING = os.environ['TPAK_DOC_CONNECTION_STRING']
TPAK_BE_IP = os.environ['TPAK_BE_IP']
TPAK_SIMI_IP = os.environ['TPAK_SIMI_IP']
#Настройки для офисных стендов
#75
BE_IP_75 = os.environ['BE_IP_75']
ORACLE_75 = os.environ['ORACLE_75']
SIMI_IP_75 = os.environ['SIMI_IP_75']
#71
BE_IP_71 = os.environ['BE_IP_71']
ORACLE_71 = os.environ['ORACLE_71']
SIMI_IP_71 = os.environ['SIMI_IP_71']
#73
BE_IP_73 = os.environ['BE_IP_73']
ORACLE_73 = os.environ['ORACLE_73']
SIMI_IP_73 = os.environ['SIMI_IP_73']


#Для валидации строки с артефактами загрузки в ДЕВ
CORRECT_ARTIFACTS = ['cct','vis','tmpl']
DUTY_OWNER = '[Александр Бауман][tg://user?id=753785354]'

STAND_75 = {
    "75":[
    f'--document-registry-url jdbc:oracle:thin:@{ORACLE_75}',
	f'--document-registry-username {DEFAULT_ORACLE_USER}',
	f'--document-registry-password {DEFAULT_ORACLE_PASS}',
	f'--think-ehr-rest-url http://{BE_IP_75}:8081',
	f'--think-ehr-rest-username {READ_MARAND_USER}',
	f'--think-ehr-rest-password {READ_MARAND_PASS} ',
	f'--simi-diagnostics-web-service-v1-url http://{SIMI_IP_75}:8080/Simi2Soap/DiagnosticsWebService/v1/Endpoint?wsdl'
    ]
}

STAND_71 = {
    "71":[
    f'--document-registry-url jdbc:oracle:thin:@{ORACLE_71}',
	f'--document-registry-username {DEFAULT_ORACLE_USER}',
	f'--document-registry-password {DEFAULT_ORACLE_PASS}',
	f'--think-ehr-rest-url http://{BE_IP_71}:8081',
	f'--think-ehr-rest-username {READ_MARAND_USER}',
	f'--think-ehr-rest-password {READ_MARAND_PASS} ',
	f'--simi-diagnostics-web-service-v1-url http://{SIMI_IP_71}:8080/Simi2Soap/DiagnosticsWebService/v1/Endpoint?wsdl'
    ]
}
STAND_73 = {
    "73":[
    f'--document-registry-url jdbc:oracle:thin:@{ORACLE_73}',
	f'--document-registry-username {DEFAULT_ORACLE_USER}',
	f'--document-registry-password {DEFAULT_ORACLE_PASS}',
	f'--think-ehr-rest-url http://{BE_IP_73}:8081',
	f'--think-ehr-rest-username {READ_MARAND_USER}',
	f'--think-ehr-rest-password {READ_MARAND_PASS} ',
	f'--simi-diagnostics-web-service-v1-url http://{SIMI_IP_73}:8080/Simi2Soap/DiagnosticsWebService/v1/Endpoint?wsdl'
    ]
}


mpak = {
	"mpak":[
	f'--document-registry-url jdbc:oracle:thin:@{MPAK_DOC_CONNECTION_STRING}',
	f'--document-registry-username {DEFAULT_ORACLE_USER}',
	f'--document-registry-password {DEFAULT_ORACLE_PASS}',
	f'--think-ehr-rest-url http://{MPAK_BE_IP}:8081',
	f'--think-ehr-rest-username {DEFAULT_MARAND_USER}',
	f'--think-ehr-rest-password {DEFAULT_MARAND_PASS} ',
	f'--simi-diagnostics-web-service-v1-url http://{MPAK_SIMI_IP}:8080/Simi2Soap/DiagnosticsWebService/v1/Endpoint?wsdl'
	]
}

dev = {"dev": [
	f'--document-registry-url jdbc:oracle:thin:@{DEV_DOC_CONNECTION_STRING}',
	f'--document-registry-username {DEFAULT_ORACLE_USER}',
	f'--document-registry-password {DEFAULT_ORACLE_PASS}',
	f'--think-ehr-rest-url http://{DEV_BE_IP}:8081 ',
	f'--think-ehr-rest-username {DEFAULT_MARAND_USER} ',
	f'--think-ehr-rest-password {DEFAULT_MARAND_PASS}',
	f'--simi-diagnostics-web-service-v1-url http://{DEV_SIMI_IP}:8080/Simi2Soap/DiagnosticsWebService/v1/Endpoint?wsdl',
]
, "dev_read":
[
	f'--document-registry-url jdbc:oracle:thin:@{DEV_READ_DOC_CONNECTION_STRING}',
	f'--document-registry-username {DEFAULT_ORACLE_USER}',
	f'--document-registry-password {DEFAULT_ORACLE_PASS}',
	f'--think-ehr-rest-url http://{DEV_READ_BE_IP}:8081 ',
	f'--think-ehr-rest-username {READ_MARAND_USER} ',
	f'--think-ehr-rest-password {READ_MARAND_PASS}',
	f'--simi-diagnostics-web-service-v1-url http://{DEV_READ_SIMI_IP}:8080/Simi2Soap/DiagnosticsWebService/v1/Endpoint?wsdl',
]
}

predppak = {
	"predppak":[
	f'--document-registry-url jdbc:oracle:thin:@{PREDPPAK_DOC_CONNECTION_STRING}',
	f'--document-registry-username {DEFAULT_ORACLE_USER}',
	f'--document-registry-password {DEFAULT_ORACLE_PASS}',
	f'--think-ehr-rest-url http://{PREDPPAK_BE_IP}:8081',
	f'--think-ehr-rest-username {DEFAULT_MARAND_USER}',
	f'--think-ehr-rest-password {DEFAULT_MARAND_PASS} ',
	f'--simi-diagnostics-web-service-v1-url http://{PREDPPAK_SIMI_IP}:8080/Simi2Soap/DiagnosticsWebService/v1/Endpoint?wsdl',
],

	"predppak_read":[
	f'--document-registry-url jdbc:oracle:thin:{PREDPPAK_READ_DOC_CONNECTION_STRING}',
	f'--document-registry-username {DEFAULT_ORACLE_USER}',
	f'--document-registry-password {DEFAULT_ORACLE_PASS}',
	f'--think-ehr-rest-url http:/{PREDPPAK_READ_BE_IP}:8081',
	f'--think-ehr-rest-username {READ_MARAND_USER}',
	f'--think-ehr-rest-password {READ_MARAND_PASS}',
	f'--simi-diagnostics-web-service-v1-url http://{PREDPPAK_READ_SIMI_IP}:8080/Simi2Soap/DiagnosticsWebService/v1/Endpoint?wsdl',
]
}

tpak = {
	"tpak":[
	f'--document-registry-url jdbc:oracle:thin:@{TPAK_DOC_CONNECTION_STRING}',
	f'--document-registry-username {DEFAULT_ORACLE_USER}',
	f'--document-registry-password {DEFAULT_ORACLE_PASS}',
	f'--think-ehr-rest-url http://{TPAK_BE_IP}:8081',
	f'--think-ehr-rest-username {DEFAULT_MARAND_USER}',
	f'--think-ehr-rest-password {DEFAULT_MARAND_PASS}',
	f'--simi-diagnostics-web-service-v1-url http://{TPAK_SIMI_IP}:8080/Simi2Soap/DiagnosticsWebService/v1/Endpoint?wsdl'
]
}


stand_list = {"dev": dev, "predppak": predppak, "tpak":tpak, "mpak": mpak, "73": STAND_73, "75":STAND_75, "71":STAND_71}

