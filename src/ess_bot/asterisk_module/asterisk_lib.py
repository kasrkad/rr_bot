import requests
from .asterisk_config import ASTERISK_PASS,ASTERISK_LOGIN,ASTERISK_IP
from ..logger_config.logger_data import create_logger
from ..bot_exceptions.asterisk_exceptions import FailAcceptNewDutyPhone,FailToChangeDutyPhone

asterisk_logger = create_logger(__name__)


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

def set_duty_phone(phone_for_set:str):
    """Обновляе переадресацию на телефон дежурного 

    Args:
        phone_for_set (str): телефон дежурного 

    Raises:
        FailToChangeDutyPhone: Не получилось обновить телефон дежурного, на новый
        FailAcceptNewDutyPhone: не получилось применить настройки телефона для нового дежурного
    """
    ASTERISK_GROUP = f'https://{ASTERISK_IP}/config.php?display=ringgroups&extdisplay=GRP-627'
    ASTERSK_HEADERS = {'Referer':'https://pbx/config.php?display=ringgroups&extdisplay=GRP-627'}
    ASTERISK_LOGIN_DATA = {"input_user": ASTERISK_LOGIN, "input_pass": ASTERISK_PASS, "submit_login": "Submit"}
    try:
        asterisk_logger.info(f"Запрос на смену номера дежурного в Asterisk на {phone_for_set}")
        payload_for_set = ASTERISK_PAYLOAD
        payload_for_set['grplist'] = f'phone_for_set'
        reload_asterisk_settings_data = {"handler": "reload"}
        request_session = requests.Session()
        auth = request_session.post(f'https://{ASTERISK_IP}/index.php',data=ASTERISK_LOGIN_DATA,
                                    verify=False)
        set_duty_phone_request = request_session.post(ASTERISK_GROUP, data=payload_for_set,cookies=request_session.cookies,
                                        headers=ASTERSK_HEADERS,
                                        verify=False,
                                        allow_redirects=True)
        if set_duty_phone_request.status_code != 200:
            asterisk_logger.error(f'Ошибка при смене номера дежурного код - {set_duty_phone_request.status_code}')
            raise FailToChangeDutyPhone('Ошибка при смене номера дежурного')
        reload_asterisk_settings = request_session.post(ASTERISK_GROUP, data=reload_asterisk_settings_data, verify=False)
        if reload_asterisk_settings.status_code != 200:
            asterisk_logger.error(f'Ошибка при примененнии номера дежурного код - {reload_asterisk_settings.status_code}')
            raise FailAcceptNewDutyPhone('Ошибка при примененнии номера дежурного код')
        asterisk_logger.info("Запрос успешно обработан")
    except Exception as exc:
        asterisk_logger.error("Произошла ошибка при смене номера дежурного",exc_info=True)
        raise Exception("Ошибка при смене номера дежуного")
        