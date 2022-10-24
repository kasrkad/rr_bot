import requests

asterisk_logger = logging.getLogger('asterisk_logger')
asterisk_logger_formatter = logging.Formatter(
    "%(name)s %(asctime)s %(levelname)s %(message)s")
asterisk_logger.setLevel(logging.INFO)
asterisk_logger_handler_file = logging.FileHandler("service_work.log", 'a')
asterisk_handler_file.setLevel(logging.INFO)
asterisk_handler_file.setFormatter(asterisk_logger_formatter)

ASTERISK_GROUP = 'https://pbx/config.php?display=ringgroups&extdisplay=GRP-627'

ASTERSK_HEADERS = {'Referer':'https://pbx/config.php?display=ringgroups&extdisplay=GRP-627'}

ASTERISK_LOGIN = {"input_user": ASTERISK_LOGIN, "input_pass": ASTERISK_PASS, "submit_login": "Submit"}

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

def set_duty_phone(str:phone_for_set):
    try:
        asterisk_logger.info(f"Запрос на смену номера дежурного в Asterisk на {phone_for_set}")
        payload_for_set = ASTERISK_PAYLOAD
        payload_for_set['grplist'] = f'phone_for_set'
        reload_asterisk_settings_data = {"handler": "reload"}
        request_session = request.Session()
        auth = request_session.post('https://pbx/index.php',data=ASTERISK_LOGIN,
                                    verify=False)
        set_duty_phone_request = request_seesion.post(ASTERISK_GROUP, data=payload,cookies=r.cookies,
                                        headers=ASTERSK_HEADERS,
                                        verify=False,
                                        allow_redirects=True)
        reload_asterisk_settings = request_session.post(ASTERISK_GROUP, data=ring_reload, verify=False)
        asterisk_logger.info("Запрос успешно обработан")
    except Exception as exc:
        asterisk_logger.error("Произошла ошибка при смене номера дежурного")
        raise Exception("Ошибка при смене номера дежуного")
        