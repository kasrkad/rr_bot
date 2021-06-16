#!/bin/python3
import json

replace_list = [
    '_{_VALUE_}_request',
    '_{_VALUE_}_4',
    '_{_VALUE_}_AS203',
    '_{_VALUE_}_In work',
    '_{_VALUE_}_AS346'
]

def parse_hpsm(file):
    with open (file, 'r') as html_file:
        for line in html_file.readlines():
            line = line.strip()
            if line.startswith('data:'):
                for replace in replace_list:
                    line = line.replace(replace,'')
                data_dict = json.loads(line[6:len(line)-1])
                data_dict = data_dict['model']['instance']
                for row in data_dict:
                    print (f'Код-заявки: {row["record_id"]}, Статус заявки: {row["status"]}, Группа:{row["group"]}, Тип заявки: {row["itemType"]}, Назначено: {row["assignee"]}, Приоритет: {row["priority"]}, Истечение срока: {row["em_next_ola_breach"]}')
                print(f'Общее кол-во заявок: {len(data_dict)}')
