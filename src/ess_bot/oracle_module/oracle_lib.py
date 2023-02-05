import oracledb
import os
import csv
from ..logger_config.logger_data import create_logger

#logger settings
oracle_module_logger = create_logger(__name__)


class OracleConnect:
    def __init__(self, connection_string= None,oracle_user = None, oracle_password = None):
        self.oracle_connection_string = connection_string
        self.oracle_user = oracle_user
        self.oracle_password = oracle_password
        
    def __enter__(self):
        try:
            self.oracle_connection = oracledb.connect(user=self.oracle_user,password=self.oracle_password,
                                                        dsn=self.oracle_connection_string, encoding='UTF-8')
            oracle_module_logger.info("Соединение с бд установлено")
            return self.oracle_connection.cursor()
        except Exception as exc:
            oracle_module_logger.error(f'Произошла ошибка при соединении с {self.oracle_connection_string}', exc_info=True)
            self.__exit__()

    def __exit__(self, type, value, traceback):
        self.oracle_connection.commit()
        self.oracle_connection.close()
        oracle_module_logger.info("Соединение с бд закрыто")


def get_audit_for_document(oracle_connection_string,oracle_user=None,oracle_password= None, documents = list):
    os.makedirs("audit_files", exist_ok=True)
    oracle_module_logger.info(f'Производим запрос на аудит документа/ов: {",".join(doc for doc in documents)}')
    audit_path_for_send = []
    with OracleConnect(oracle_connection_string,oracle_user=oracle_user, oracle_password=oracle_password) as cursor:
        for doc in documents:
            try:
                data = cursor.execute(f"""SELECT * FROM AUDIT_RECORD WHERE DOCUMENT_ID = '{doc.strip()}' ORDER BY EVENT_TIME ASC""").fetchall()
                column_names = [c[0] for c in cursor.description]
                if data:
                    with open(f'./audit_files/{doc}.csv', 'w', encoding='utf-8') as out_file:
                        out_file.write('sep=,\n')
                        csv_writer = csv.DictWriter(out_file, column_names, extrasaction='raise', dialect='excel')
                        csv_writer.writeheader()
                        csv_writer.writerows([dict(zip(column_names,d)) for d in data])
                        audit_path_for_send.append(f'./audit_files/{doc}.csv') 
            except Exception as exc:
                oracle_module_logger.error(f'Произошла ошибка при запросе аудита {doc}', exc_info=True)
                raise Exception
    return audit_path_for_send


def get_document_metadata_status(oracle_connection_string, oracle_user=None,oracle_password=None, documents = list):
    oracle_module_logger.info(f'Был запрошен статус документов {"".join(doc.strip() for doc in documents)}')
    documents_metadata = {}
    with OracleConnect(oracle_connection_string, oracle_user=oracle_user, oracle_password=oracle_password)as cursor:
        for doc in documents:
            try:
                data = cursor.execute(f"""select id, CASE STATUS WHEN 2 then 'Подписан' when 3 then 'Аннулирован' when 1 then 'Черновик' when 0 then 'Создан' END from METADATA where id = '{doc.strip()}'""").fetchone()
                if data:
                    documents_metadata[doc.strip()] = data[1]
                else:
                    documents_metadata[doc.strip()] = "Не найден"
            except Exception as exc:
                oracle_module_logger.error(f'Произошла ошибка при запросе статуса документа {doc.strip()}', exc_info=True)
                raise Exception
    return documents_metadata
