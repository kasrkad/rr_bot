import requests
import os
import logging

request_to_simi_logger = logging.getLogger('request_to_simi_logger')
request_to_simi_logger_formatter = logging.Formatter(
    "%(name)s %(asctime)s %(levelname)s %(message)s")
request_to_simi_logger.setLevel(logging.INFO)

request_to_simi_logger_handler_file = logging.FileHandler("simi_request.log", 'a')
request_to_simi_logger_handler_file.setLevel(logging.INFO)
request_to_simi_logger_handler_file.setFormatter(request_to_simi_logger_formatter)
request_to_simi_logger.addHandler(request_to_simi_logger_handler_file)




PRODUCER_SOAP_PASS = os.environ['PRODUCER_SOAP_PASS']
PRODUCER_SOAP_USER = os.environ['PRODUCER_SOAP_USER']
SIMI_DNS_NAME_ENDPOINT_TEMPLATE = os.environ['SIMI_DNS_NAME_ENDPOINT_TEMPLATE']
HEADERS = headers = {'content-type': 'text/xml'}

def set_diagnostic_endpoint_request(request_to_set, state = False):
    try:
        request_body = request_to_set.format(state=state)
        request_to_simi_logger.info(f'Отправлен запрос на изменение {request_to_set} параметра на {state}')
        for node_num in range(1,13):
            url = SIMI_DNS_NAME_ENDPOINT_TEMPLATE.format(i=node_num)
            # response = requests.post(url, data=request_body, headers=HEADERS)
        request_to_simi_logger.info(f"Параметр {state} установлен")
        raise Exception("Очеень страшний ошибпка!11")
    except Exception as exc:
        request_to_simi_logger.error(f"Произошла ошибка при установлении параметра {request_to_simi_logger}", exc_info=True)
        raise
