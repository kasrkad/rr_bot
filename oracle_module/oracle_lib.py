import cx_Oracle
import os
import logging
import csv


oracle_module_logger = logging.getLogger('oracle_module_logger')
oracle_module_logger_formatter = logging.Formatter(
    "%(name)s %(asctime)s %(levelname)s %(message)s")
oracle_module_logger.setLevel(logging.INFO)
oracle_module_logger_handler_file = logging.FileHandler("oracle_module.log", 'a')
oracle_module_logger_handler_file.setLevel(logging.INFO)
oracle_module_logger_handler_file.setFormatter(oracle_module_logger_formatter)
oracle_module_logger.addHandler(oracle_module_logger_handler_file)


DEFAULT_ORACLE_USER = os.environ['DEFAULT_ORACLE_USER']
DEFAULT_ORACLE_PASS = os.environ['DEFAULT_ORACLE_PASS']

class OracleConnect:
    def __init__(self, connection_string= None):
        self.oracle_connection_string = connection_string
        
    def __enter__(self):
        try:
            self.oracle_connection = cx_Oracle.connect(DEFAULT_ORACLE_USER,DEFAULT_ORACLE_PASS, self.oracle_connection_string, encoding='UTF-8')
            oracle_module_logger.info("Соединение с бд установлено")
            return oracle_connection.cursor()
        except Exception as exc:
            oracle_module_logger.error(f'Произошла ошибка при соединении с {self.oracle_connection_string}', exc_info=True)
            self.__exit__()

    def __exit__(self, type, value, traceback):
        self.oracle_connection.commit()
        self.oracle_connection.close()
        oracle_module_logger.info("Соединение с бд закрыто")


def get_audit_for_document(oracle_connection_string, documents = list):
    os.makedirs("audit_files", exist_ok=True)
    oracle_module_logger.info(f'Производим запрос на аудит документа/ов: {",".join(doc for doc in documents)}')
    audit_path_for_send = []
    with OracleConnect(oracle_connection_string) as cursor:
            for doc in documents:
                try:
                    data = cursor.execute(f"""SELECT * FROM AUDIT_RECORD WHERE DOCUMENT_ID = '{doc.strip()}' ORDER BY EVENT_TIME ASC""").fetchall()
                    column_names = [c[0] for c in cursor.description]
                    with open(f'./audit_files/{doc}.csv', 'w', encoding='utf-8') as out_file:
                        out_file.write('sep=,\n')
                        csv_writer = csv.DictWriter(out_file, column_names, extrasaction='raise', dialect='excel')
                        csv_writer.writeheader()
                        csv_writer.writerows([dict(zip(column_names,d)) for d in data])
                except Exception as exc:
                    oracle_module_logger.error(f'Произошла ошибка при запросе аудита {doc}', exc_info=True)
