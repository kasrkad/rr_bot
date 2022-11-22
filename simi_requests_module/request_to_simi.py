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


def simi_document_request(request_to_simi, stand_node_adress, documents_ids=list, requester_tg_id=None) -> dict:
    request_to_simi_logger.info(f'Пользователем {requester_tg_id} запрошены документы {",".join(doc for doc in documents_ids)}.')
    docs_with_content = {}
    for doc_id in documents_ids:
        try:
            request_body = request_to_simi.format(id=doc_id.strip(),
                                                tg=requester_tg_id,
                                                PPAK_SOAP_USER=PPAK_SOAP_USER)
            query_result = requests.post(stand_node_adress,
                                        data = request_body,
                                        headers =HEADERS)
            if query_result.status_code == 200:
                docs_with_content[doc_id.strip()] = query_result.text                
        except Exception as exc:
            request_to_simi_logger.error(f"Произошла ошибка при работе с документом {doc_id}", exc_info=True)
    request_to_simi_logger.info(f'Документы переданы успешно {",".join(doc for doc in documents_ids)}.')
    return docs_with_content


def write_json_or_xml_document(doc_data = dict, file_format = 'xml'):
    request_to_simi_logger.info(f'Записываем в {file_format} документы {",".join(doc_id for doc_id in doc_data.keys())}.')
    os.makedirs('./docs_xml/', exist_ok=True)
    os.makedirs('./docs_json/', exist_ok=True)
    path_way_for_files = []
    for doc_id, doc_content in doc_data.items():
        try:
            if file_format == 'xml':
                with open(f"./docs_xml/{doc_id}.xml", "wb+") as id_file:
                    id_file.write(doc_content.encode('utf-8').strip())
                path_way_for_files.append(f'./docs_xml/{doc_id}.xml')
            elif file_format == 'json':
                with open(f"./docs_json/{doc_id}.json", "w") as json_for_write:
                    json.dump(json_for_write,doc_content, ensure_ascii=False , indent=2)
                path_way_for_files.append(f'./docs_json/{doc_id}.json')
        except Exception as exc:
            request_to_simi_logger.info(f'Произошла ошибка при записи документа {doc_id} в формате {file_format}.')
    return path_way_for_files 


def base64_decode_to_json(doc_data = dict):
    pass