import requests
import os
from .request_config import *
from ..logger_config.logger_data import create_logger

#configure logger
request_to_simi_logger = create_logger(__name__)


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
            response = requests.post(request_to_get, data=request_to_get, headers=HEADERS)
            if "true" in response.text:
                request_nodes_result[url] = True
            else:
                request_nodes_result[url] = False
        except Exception as exc:
            request_to_simi_logger.error(f'Произошла ошибка при запросе на узле {url}', exc_info=True)
            request_nodes_result[url] = "error, see logs"
    
    for node_num_simi_asinc in range(1,3):
        url = SIMIP3_DNS_NAME_ENDPOINT_TEMPLATE.format(i=node_num_simi_asinc)
        try:
            response = requests.post(request_to_get, data=request_to_get, headers=HEADERS)
            if "true" in response.text:
                request_nodes_result[url] = True
            else:
                request_nodes_result[url] = False
        except Exception as exc:
            request_to_simi_logger.error(f'Произошла ошибка при запросе на узле {url}', exc_info=True)
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
            request_nodes_result[url] = 600
            request_to_simi_logger.error(f"Произошла ошибка при запросе на пересоздание продьюсера на узле {url}", exc_info=True)
    
    for node_num_simi_asinc in range(1,3):
        url = SIMIP3_DNS_NAME_ENDPOINT_TEMPLATE.format(i=node_num_simi_asinc)
        try:
            response = requests.post(url, data=request_body, headers=HEADERS)
            request_nodes_result[url] = response.status_code
        except Exception as exc:
            request_nodes_result[url] = 600
            request_to_simi_logger.error(f"Произошла ошибка при запросе на пересоздание продьюсера на узле {url}", exc_info=True)
    
    return request_nodes_result


def simi_document_request(request_to_simi, stand_node_adress, documents_ids, requester_tg_id=None) -> dict:
    request_to_simi_logger.info(f'Пользователем {requester_tg_id} запрошены документы {",".join(doc for doc in documents_ids)}.')
    docs_with_content = {}
    errors = False
    for doc_id in documents_ids:
        try:
            request_body = request_to_simi.format(id=doc_id.strip(),
                                                tg=requester_tg_id,
                                                PPAK_SOAP_USER=PPAK_SOAP_USER)
            query_result = requests.post(f'{stand_node_adress}/SimiService/v5/Endpoint',
                                        data = request_body,
                                        headers =HEADERS)
            if query_result.status_code == 200:
                docs_with_content[doc_id.strip()] = query_result.text                
        except Exception as exc:
            errors = True
            request_to_simi_logger.error(f"Произошла ошибка при запросе документа -  {doc_id}", exc_info=True)
    if errors:
        request_to_simi_logger.info(f'В процессе запроса документов были ошибки.')
    else:
        request_to_simi_logger.info(f'Документы переданы успешно {",".join(doc for doc in documents_ids)}.')
    return docs_with_content


def write_json_or_xml_document(doc_data = dict, file_format = 'xml'):
    import json
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
                json_data = json.loads(doc_content)
                with open(f"./docs_json/{doc_id}.json", "w") as json_for_write:
                    json.dump(json_data,json_for_write, ensure_ascii=False , indent=2)
                path_way_for_files.append(f'./docs_json/{doc_id}.json')
        except Exception as exc:
            request_to_simi_logger.info(f'Произошла ошибка при записи документа {doc_id} в формате {file_format}.', exc_info=True)
    return path_way_for_files 


def base64_decode_to_json(request_to_convert,request_to_simi, stand_node_adress, documents_ids:list, requester_tg_id=None):
    from bs4 import BeautifulSoup
    comositions = {}
    request_to_simi_logger.info(f'Запрашиваем документы для расшифровки композиции')
    documents_with_data = simi_document_request(request_to_simi=request_to_simi,stand_node_adress=stand_node_adress,
                                                     documents_ids=documents_ids, requester_tg_id=requester_tg_id)
    for document_id, document_data in documents_with_data.items():
        request_to_simi_logger.info(f'Преобразовываем данные из документа {document_id}')
        try:
            xml_document = BeautifulSoup(document_data, 'xml')
            xml_document.find('soap:Body')
            composition_data = xml_document.find('doc:data')
            if composition_data:
                base64_for_convert = composition_data.contents[0]
                request_for_convert = requests.post(f'{stand_node_adress}/OpenEhrService/v4/Endpoint',
                                                     data=request_to_convert.format(doc_base64=base64_for_convert), headers=HEADERS)
                   
            xml_response_for_convert = BeautifulSoup(request_for_convert.text, 'xml') #ЭТО ЧТОБЫ ВЫТАЩИТЬ ТОЛЬКО ПРЕОБРАЗОВАНИЕ BASE64
            xml_response_for_convert.find('soap:Body')
            json_from_response = xml_response_for_convert.find('ns6:structuredJson')
            comositions[document_id] = json_from_response.contents[0]
            request_to_simi_logger.info(f'Документ {document_id} успешно преобразован')
        except Exception as exc:
            request_to_simi_logger.info(f'Во время преобразования документа {document_id} произошли ошибки')
    return comositions
