#!/bin/python3
import os
import json
import requests
import re
import config
import datetime
import pathlib


path = pathlib.Path().absolute()
pattern = r"[a-z0-9]{8}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{12}"

def check_permission(message, users):
    if str(message.from_user.id) not in users.keys():
        raise ValueError(f"{message.from_user.last_name} {message.from_user.first_name} не имеет право давать боту комманды", message.from_user.id)


def check_working_time():
    """[Проверяет время и возвращает True False]

    Returns:
        [type]: [description]
    """
    work_hours = datetime.datetime.now()
    hours = int(work_hours.strftime("%H"))
    minutes = int(work_hours.strftime("%M"))
    with open('check_time.log', 'w', encoding='utf8') as time_file:
        time_file.write(f'last check in {hours} hours {minutes} minutes')
    if hours >= 10 and hours <= 22:
        return True
    return False


def write_cct_log(commit=None, user_id=None):
    date = datetime.datetime.today().strftime("%Y-%m-%d")
    with open('./simi_cli/ids', 'r', encoding='utf8') as ids_file:
        cct_and_artifacts = ids_file.readline()
    with open(f'{path}/cct_log/{date}', 'a', encoding='utf8') as log_file:
        log_file.write(f'{user_id} запустил загрузку {cct_and_artifacts} , commit:{commit}\n')


def remove_files(list):
    for file in list:
        os.remove(file)


def load_from_json(jsonfile):
    if os.path.exists(jsonfile):
        with open(jsonfile, 'r', encoding='utf8') as json_file:
            json_data = json.load(json_file)
        return json_data
    else:
        return None


def validate_cct_string(cct_message):
    cct = cct_message.text
    if len(cct) == 5:
        if cct.isdigit():
            return cct
    raise ValueError(f'Не корректный номер ССТ: {cct_message.text}, ССТ = 5 цифр', cct_message.chat.id)


def validate_artifact_string(artifact_message):
    artifacts = artifact_message.text
    artifacts_for_check = artifacts.split(',')
    artifacts_for_check = set(artifacts_for_check)
    for artifact in artifacts_for_check:
        if artifact.strip().lower() not in config.CORRECT_ARTIFACTS:
            raise ValueError(f'Нeкорректные данные в списке артефактов {artifact_message.text}', artifact_message.chat.id)
    return f'{",".join(x.strip().lower() for x in artifacts_for_check)}'


def validate_commit_string(commit_message):
    commit = commit_message.text
    if len(commit) == 9 and re.match(r'[a-z0-9]{9}', commit.lower()):
        write_cct_log(user_id=commit_message.from_user.id, commit=commit)
        return commit.lower()
    raise ValueError(f"Некорректный вид коммита {commit_message.text}, должно быть 9 символов, английские буквы и цифры, отсутствовать спецзнаки", commit_message.chat.id)   


def validate_dociment_id(docid_list_message):
    docid_list = docid_list_message.text.split(' ')
    if len(docid_list) > 1:
        out_list = []
        for id in docid_list[1:]:
            if len(id) == 36 and re.match(r'[a-z0-9]{8}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{12}', id.lower().strip()):
                out_list.append(id.lower().strip())
            else:
                raise ValueError(f'ID документа {id} некорректный: возможны пропущенные буквы, кирилические символы, спецсимволы.\nПример: f930e251-c468-49e6-a889-e6db0885221a ', docid_list_message.chat.id)
        return out_list
    raise ValueError('Передан пустой список документов', docid_list_message.chat.id)


def get_document(id_, tg_user_id):
    id_ = id_.rstrip()
    body = config.REQUEST_BODY.format(id=id_, tg=tg_user_id)
    headers = {'content-type': 'text/xml'}
    response = requests.post(config.URL_FOR_DOC, data=body, headers=headers)
    with open("documents_output/" + id_ + ".xml", "wb+") as id_file:
        id_file.write(response.text.encode('utf-8').strip())
