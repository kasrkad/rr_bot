import requests
import os
import logging

#configure logger
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
SIMIP3_DNS_NAME_ENDPOINT_TEMPLATE = os.environ['SIMIP3_DNS_NAME_ENDPOINT_TEMPLATE']
HEADERS = {'content-type': 'text/xml'}


def set_request_diagnostic_endpoint(request_to_set, state = False) -> dict:
    request_body = request_to_set.format(state=state)
    request_to_simi_logger.info(f'Отправлен запрос на изменение {request_to_set} параметра на {state}')
    request_nodes_result = {}
    
    for node_num_simi in range(1,13):
        url = SIMI_DNS_NAME_ENDPOINT_TEMPLATE.format(i=node_num_simi)
        try:
            response = requests.post(url, data=request_body, headers=HEADERS)
            request_nodes_result[url] = response.status_code
        except Exception as exc:
            request_nodes_result[url] = "error, see logs"
            request_to_simi_logger.error(f"Произошла ошибка при установлении параметра {state} на узел {url}", exc_info=True)
    
    for node_num_simi_asinc in range(1,3):
        url = SIMIP3_DNS_NAME_ENDPOINT_TEMPLATE.format(i=node_num_simi_asinc)
        try:
            response = requests.post(url, data=request_body, headers=HEADERS)
            request_nodes_result[url] = response.status_code
        except Exception as exc:
            request_nodes_result[url] = "error, see logs"
            request_to_simi_logger.error(f"Произошла ошибка при установлении параметра {state} на узел {url}", exc_info=True)
    
    return request_nodes_result


def get_request_diagnostic_endpoint(request_to_get) -> dict:
    request_to_simi_logger.info(f'Отправлен запрос на проверку состояния {request_to_get}')
    request_nodes_result = {}
    
    for node_num_simi in range(1,13):
        url = SIMI_DNS_NAME_ENDPOINT_TEMPLATE.format(i=node_num_simi)
        try:
            response = requests.post(request_to_get, data=request_body, headers=HEADERS)
            if "true" in response.text:
                request_nodes_result[url] = True
            else:
                request_nodes_result[url] = False
        except Exception as exc:
            request_nodes_result[url] = "error, see logs"
    
    for node_num_simi_asinc in range(1,3):
        url = SIMIP3_DNS_NAME_ENDPOINT_TEMPLATE.format(i=node_num_simi_asinc)
        try:
            response = requests.post(request_to_get, data=request_body, headers=HEADERS)
            if "true" in response.text:
                request_nodes_result[url] = True
            else:
                request_nodes_result[url] = False
        except Exception as exc:
            request_nodes_result[url] = "error, see logs"
    
    return request_nodes_result


def producer_recreate_request(producer_recreate_request) -> dict:
    request_body = producer_recreate_request.format(soap_name=PRODUCER_SOAP_USER,
                                                    soap_pass=PRODUCER_SOAP_PASS)
    request_to_simi_logger.info(f'Отправлен запрос на пересоздание продьюсера.')
    request_nodes_result = {}
    
    for node_num_simi in range(1,13):
        url = SIMI_DNS_NAME_ENDPOINT_TEMPLATE.format(i=node_num_simi)
        try:
            response = requests.post(url, data=request_body, headers=HEADERS)
            request_nodes_result[url] = response.status_code
        except Exception as exc:
            request_nodes_result[url] = "error, see logs"
            request_to_simi_logger.error(f"Произошла ошибка при запросе на пересоздание продьюсера на узле {url}", exc_info=True)
    
    for node_num_simi_asinc in range(1,3):
        url = SIMIP3_DNS_NAME_ENDPOINT_TEMPLATE.format(i=node_num_simi_asinc)
        try:
            response = requests.post(url, data=request_body, headers=HEADERS)
            request_nodes_result[url] = response.status_code
        except Exception as exc:
            request_nodes_result[url] = "error, see logs"
            request_to_simi_logger.error(f"Произошла ошибка при запросе на пересоздание продьюсера на узле {url}", exc_info=True)
    
    return request_nodes_result


def simi_document_request(request_to_simi, stand_node_adress, documents_ids=list, requester_tg_id=None) -> list:
    if not os.path.exists("./docs/"):
        os.mkdir("./docs/")

    request_to_simi_logger.info(f'Пользователем {requester_tg_id} запрошены документы {",".join(doc for doc in documents_ids)}.')
    path_way_for_files = []
    for doc_id in documents_ids:
        try:
            request_body = request_to_simi.format(id=doc_id.strip(),
                                                tg=requester_tg_id,
                                                PPAK_SOAP_USER=PPAK_SOAP_USER)
            query_result = requests.post(stand_node_adress,
                                        data = request_body,
                                        headers =HEADERS)
            with open("./docs/documents_output/" + doc_id + ".xml", "wb+") as id_file:
                id_file.write(response.text.encode('utf-8').strip())
            path_way_for_files.append(f'./docs/{doc_id}.xml')
        except Exception as exc:
            request_to_simi_logger.error(f"Произошла ошибка при работе с документами", exc_info=True)
    
    return path_way_for_files
