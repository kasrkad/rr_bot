#!/bin/python3
import json
import datetime
import os
replace_list = [
    '_{_VALUE_}_request',
    '_{_VALUE_}_4',
    '_{_VALUE_}_AS203',
    '_{_VALUE_}_In work',
    '_{_VALUE_}_AS346'
]

def write_json(jobs_list,actual_filename,log_filename):
    line_for_json = ''
    for line in jobs_list:
        line_for_json+= str(line)+"\n"
    with open (actual_filename,"w",encoding="utf8") as monitor_file:
        monitor_file.write(line_for_json)

    with open (log_filename,'a', encoding='utf8') as log_file:
        log_file.write(line_for_json)


def parse_hpsm(file):
    date = datetime.datetime.today().strftime('%Y-%m-%d')
    time = str(datetime.datetime.now().time())
    monitor_list = []
    others_list = []
    with open (file, 'r') as html_file:
        for line in html_file.readlines():
            line = line.strip()

            if line.startswith('data:'):
                for replace in replace_list:
                    line = line.replace(replace,'')
                data_dict = json.loads(line[6:len(line)-1])
                data_dict = data_dict['model']['instance']
                
                for row in data_dict:
                    if row['record_id'].startswith(('T','C')):
                        others_list.append({'record_id':row["record_id"], 'status': row["status"], 'group':row["group"], 'itemType': row["itemType"],
                        'assignee': row["assignee"], 'priotity': row["priority"], 'sla': row["em_next_ola_breach"], 'check_time':f'{time}'})
                    else:
                        print (f'Код-заявки: {row["record_id"]}, Статус заявки: {row["status"]}, Группа:{row["group"]}, Тип заявки: {row["itemType"]}, Назначено: {row["assignee"]}, Приоритет: {row["priority"]}, Истечение срока: {row["em_next_ola_breach"]}')
                        monitor_list.append({'record_id':row["record_id"], 'status': row["status"], 'group':row["group"], 'itemType': row["itemType"],
                        'assignee': row["assignee"], 'priotity': row["priority"], 'sla': row["em_next_ola_breach"], 'check_time':f'{time}'})    
                   
                print(f'Общее кол-во заявок: {len(monitor_list)} \nOбщее кол-во работ : {len(others_list)}')
    
        write_json(monitor_list,'monitor_actual.json', f'monitor_log_for_{date}.json')
    
        write_json(others_list,f'{date} other_actual.json',f'other_log_for_{date}.json')
    
parse_hpsm('html')
