#!/bin/python3
import os

#Настройки доступа до Репозитория ССТ
SIMI_DOC_REPO_FOLDER = os.getenv('SIMI_DOC_REPO_FOLDER')
SIMI_DOC_REPO_USER = os.getenv('SIMI_DOC_REPO_USER')
SIMI_DOC_REPO_PASS = os.getenv('SIMI_DOC_REPO_PASS')
SIMI_DOC_REPO_URL = os.getenv('SIMI_DOC_REPO_URL')

#HPSM настройки
HTTP_PROXY = os.getenv('HTTP_PROXY')
HPSM_USER = os.getenv('HPSM_USER')
HPSM_PASS = os.getenv('HPSM_PASS')
HPSM_CHECK_TIME = os.getenv('HPSM_CHECK_TIME')
#Настройки бота
ECC_CHAT_ID = os.getenv('ECC_CHAT_ID')
TEST_STAND_GROUP_ID = os.getenv('TEST_STAND_GROUP_ID')
MPAK_GROUP_ID = os.getenv('MPAK_GROUP_ID')
TG_BOT_TOKEN = os.getenv('TG_BOT_TOKEN')
#Настройки скачивания документов
PPAK_SOAP_URL = os.getenv('PPAK_SOAP_URL')
PPAK_SOAP_USER = os.getenv('PPAK_SOAP_USER')
#Настройки доступа до астериска для смены номера
ASTERISK_LOGIN = os.getenv('ASTERISK_LOGIN')
ASTERISK_PASS = os.getenv('ASTERISK_PASS')
#Настройки стендов для работы с ССТ
DEFAULT_ORACLE_USER = os.getenv('DEFAULT_ORACLE_USER')
DEFAULT_ORACLE_PASS = os.getenv('DEFAULT_ORACLE_PASS')
DEFAULT_MARAND_USER = os.getenv('DEFAULT_MARAND_USER')
DEFAULT_MARAND_PASS = os.getenv('DEFAULT_MARAND_PASS')
READ_MARAND_USER = os.getenv('READ_MARAND_USER')
READ_MARAND_PASS = os.getenv('READ_MARAND_PASS')
#МПАК
MPAK_DOC_CONNECTION_STRING =os.getenv('MPAK_DOC_CONNECTION_STRING')
MPAK_BE_IP =os.getenv('MPAK_BE_IP')
MPAK_SIMI_IP =os.getenv('MPAK_SIMI_IP')
#ТЕСТ и ТЕСТ чтение
DEV_DOC_CONNECTION_STRING = os.getenv('DEV_DOC_CONNECTION_STRING')
DEV_BE_IP = os.getenv('DEV_BE_IP')
DEV_SIMI_IP = os.getenv('DEV_SIMI_IP')
DEV_READ_DOC_CONNECTION_STRING =os.getenv('DEV_READ_DOC_CONNECTION_STRING')
DEV_READ_BE_IP = os.getenv('DEV_READ_BE_IP')
DEV_READ_SIMI_IP = os.getenv('DEV_READ_SIMI_IP')
#ПРЕДППАК И ПРЕДППАК чтение
PREDPPAK_DOC_CONNECTION_STRING = os.getenv('PREDPPAK_DOC_CONNECTION_STRING')
PREDPPAK_BE_IP = os.getenv('PREDPPAK_BE_IP')
PREDPPAK_SIMI_IP = os.getenv('PREDPPAK_SIMI_IP')
PREDPPAK_READ_DOC_CONNECTION_STRING = os.getenv('PREDPPAK_READ_DOC_CONNECTION_STRING')
PREDPPAK_READ_BE_IP = os.getenv('PREDPPAK_READ_BE_IP')
PREDPPAK_READ_SIMI_IP = os.getenv('PREDPPAK_READ_SIMI_IP')
#ТПАК
TPAK_DOC_CONNECTION_STRING = os.getenv('TPAK_DOC_CONNECTION_STRING')
TPAK_BE_IP = os.getenv('TPAK_BE_IP')
TPAK_SIMI_IP = os.getenv('TPAK_SIMI_IP')


#Для валидации строки с артефактами загрузки в ДЕВ
CORRECT_ARTIFACTS = ['cct','vis','tmpl']
DUTY_OWNER = '[Александр Бауман](tg://user?id=753785354)'

#Для скачивания документов

REQUEST_BODY = """<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope" xmlns:user="http://emias.mos.ru/system/v1/userContext/" xmlns:typ="http://emias.mos.ru/simi/simiService/v5/types/" xmlns:v5="http://emias.mos.ru/simi/document/v5/" xmlns:v51="http://emias.mos.ru/simi/core/v5/">
   <soap:Header>
    <wsse:Security xmlns:wsse="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd" xmlns:wsu="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd">
        <wsse:UsernameToken wsu:Id="UsernameToken-50">
            <wsse:Username>{PPAK_SOAP_USER}</wsse:Username>           
        </wsse:UsernameToken>
    </wsse:Security>
    <user:userContext>
        <user:systemName>SIMI</user:systemName>
        <user:userName>simi_support/tg:{tg}</user:userName>
        <user:userRoleId>1</user:userRoleId>
    </user:userContext>
</soap:Header>
   <soap:Body>
      <typ:getDocumentRequest>
         <v5:documentId>{id}</v5:documentId>
         <!--Optional:-->
            </typ:getDocumentRequest>
   </soap:Body>
</soap:Envelope>"""

ASTERISK_PAYLOAD = {
"display": "ringgroups",
"action": "edtGRP",
"account": "627",
"description": "EMIAS-duty",
"strategy": "ringall",
"grptime": "20",
"annmsg_id": None,
"ringing": "Ring",
"grppre": None,
"alertinfo": None,
"remotealert_id": None,
"toolate_id": None,
"changecid": "default",
"recording": "dontcare",
"goto0": "Ring_Groups",
"Ring_Groups0": "ext-group,628,1",
"Submit": "Submit Changes"
}

ASTERISK_GROUP = 'https://pbx/config.php?display=ringgroups&extdisplay=GRP-627'

ASTERSK_HEADERS = {'Referer':'https://pbx/config.php?display=ringgroups&extdisplay=GRP-627'}

ASTERISK_LOGIN = {"input_user": ASTERISK_LOGIN, "input_pass": ASTERISK_PASS, "submit_login": "Submit"}


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
	f'--think-ehr-rest-username {DEFAULT_MARAND_USER} '
	f'--think-ehr-rest-password {DEFAULT_MARAND_PASS}',
	f'--simi-diagnostics-web-service-v1-url http://{DEV_SIMI_IP}:8080/Simi2Soap/DiagnosticsWebService/v1/Endpoint?wsdl',
]
, "dev_read":
[
	f'--document-registry-url jdbc:oracle:thin:@{DEV_READ_DOC_CONNECTION_STRING}',
	f'--document-registry-username {DEFAULT_ORACLE_USER}',
	f'--document-registry-password {DEFAULT_ORACLE_PASS}',
	f'--think-ehr-rest-url http://{DEV_READ_BE_IP}:8081',
	f'--think-ehr-rest-username {READ_MARAND_USER}',
	f'--think-ehr-rest-password {READ_MARAND_PASS}',
	f'--simi-diagnostics-web-service-v1-url http://:{DEV_READ_SIMI_IP}:8080/Simi2Soap/DiagnosticsWebService/v1/Endpoint?wsdl',
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


stand_list = {"dev": dev, "predppak": predppak, "tpak":tpak, "mpak": mpak}
