#!/bin/python3
import os
import subprocess
import telebot
import config
import json
import bot_functions
import glob
import re
import datetime


rr_bot = telebot.TeleBot(config.BOT_TOKEN, parse_mode='MARKDOWN')
global duty_eng
duty_eng = bot_functions.load_from_json('duty.json')
global users
users = bot_functions.load_from_json('users.json')


@rr_bot.message_handler(regexp=bot_functions.pattern)
def handle_message(message):
    try:
        bot_functions.check_permission(message, users)
        docs_from_forward = re.findall(bot_functions.pattern, message.text)
        for doc in docs_from_forward:
            with open('./doc_download_log/log.txt', 'a', encoding='utf8') as doc_log:
                doc_log.write(f"{doc} скачан пользователем {message.from_user.first_name} {message.from_user.last_name} - id {message.from_user.id}\n")
            bot_functions.get_document(doc, message.from_user.id)
            document = open(f'./documents_output/{doc}.xml')
            rr_bot.send_document(message.from_user.id, document)
            os.remove(f'./documents_output/{doc}.xml')
    except ValueError as exc:
        rr_bot.send_message(exc.args[1], exc.args[0])


@rr_bot.message_handler(commands=['cct'])
def artifact_download_dev(message):  # грузит только на дев и только с коммита
    try:
        bot_functions.check_permission(message, users)
        msg = rr_bot.reply_to(message, "введите ссt")
        rr_bot.register_next_step_handler(msg, cct_enter_step)
    except ValueError as exc:
        rr_bot.send_message(exc.args[1], exc.args[0])
    except Exception as exc:
        print(exc)


def cct_enter_step(message):
    try:
        cct = bot_functions.validate_cct_string(message)
        with open('./simi_cli/ids', 'w', encoding='utf8') as enter_cct_file:
            enter_cct_file.write(f"{cct}; ")
        msg = rr_bot.reply_to(message, "Введите параметры загрузки артефактов в формате simicli : cct, vis, tmpl.\n Пример: cct, vis ")
        rr_bot.register_next_step_handler(msg, artifact_enter_step)
    except ValueError as exc:
        rr_bot.send_message(exc.args[1], exc.args[0])
    except Exception as exc:
        print(exc)
        return

def artifact_enter_step(message):
    try:
        artifacts = bot_functions.validate_artifact_string(message)
        print(artifacts)
        with open('./simi_cli/ids', 'a', encoding='utf8') as enter_artifacts_file:
            enter_artifacts_file.write(artifacts)
        msg = rr_bot.reply_to(message, "Введите коммит: \nПример: 81dsf93")
        rr_bot.register_next_step_handler(msg, simi_cli_check_and_start)
    except ValueError as exc:
        rr_bot.send_message(exc.args[1], exc.args[0])
    except Exception as exc:
        print(exc)
        return

def simi_cli_check_and_start(message):
    global commit
    try:
        commit = bot_functions.validate_commit_string(message)
        with open('./simi_cli/ids', 'r', encoding='utf8') as check_ids_file:
            simi_cli_ids = check_ids_file.readline()
        msg = rr_bot.reply_to(message, f"Проверьте настройки для simicli,\nДля загрузки: {simi_cli_ids},\nCommit: {commit}\nЕсли все корректно, введите Y")
        rr_bot.register_next_step_handler(msg, start_cli)
    except ValueError as exc:
        print(exc.args)
        rr_bot.send_message(exc.args[1], exc.args[0])
    except Exception as exc:
        print(exc)
        return

def start_cli(message):
    answer = message.text
    if answer.strip() == 'Y':
        rr_bot.send_message(message.chat.id, f"Стартуем simicli с параметрами: applycommit dev {commit}")
        out = subprocess.Popen(['./simi_cli/artifact.sh', 'applycommit', 'dev', commit], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        out.wait()
        logs_for_send = glob.glob('./logs/*log.txt')
        rr_bot.send_message(message.chat.id, "Лови логи")
        for files in logs_for_send:
            doc = open(files)
            rr_bot.send_document(message.from_user.id, doc)
        bot_functions.remove_files(glob.glob("./logs/*"))
    else:
        rr_bot.send_message(message.chat.id, "Запуск отменен, переделывай.")


@rr_bot.message_handler(commands=['help'])
def print_help(message):
    rr_bot.reply_to(message, " Владею нюндзюцу:\n /help : выведу это сообщение,\n /дежурю или /дежурный : регистрирую как дежурного инженера,\n /ктоДежурит: укажу на дежурного инженера,\nПришли в личку docID : скачаю с ППАК документ и пришлю его.\n/cct: загружу cct по коммиту в ТЕСТ", parse_mode="MARKDOWN")


@rr_bot.message_handler(commands=['дежурю', 'Дежурю', 'Дежурный', 'дежурный'])
def get_duty_id(message):
    try:
        bot_functions.check_permission(message, users)
        global duty_eng
        rr_bot.send_message(config.CHAT_ID, f'Дежурный зарегистрирован - [{message.from_user.first_name} {message.from_user.last_name}](tg://user?id={message.from_user.id}), номер переключен')
        rr_bot.send_message(config.CHAT_ID, f'Предыдущий дежурный - [{duty_eng["first_name"]} {duty_eng["last_name"]}](tg://user?id={duty_eng["t_id"]})')
        duty_eng = {"t_id": message.from_user.id, "first_name": message.from_user.first_name, "last_name": message.from_user.last_name}
        bot_functions.change_duty_phone(duty_eng["t_id"], users)
        with open('duty.json', 'w', encoding='utf8') as duty_file:
            json.dump(duty_eng, duty_file, ensure_ascii=False)
    except Exception as exc:
        rr_bot.send_message(exc.args[1], exc.args[0])

@rr_bot.message_handler(commands=['КтоДежурит', 'ктодежурит', 'ктоДежурит'])
def who_duty_today(message):
    global duty_eng
    if duty_eng:
        rr_bot.reply_to(message, f"Сегодня дежурит [{duty_eng['first_name']} {duty_eng['last_name']}](tg://user?id={duty_eng['t_id']})")
    else:
        rr_bot.reply_to(message, f"Дежурный не обнаружен, вызываем ответственного: {config.DUTY_OWNER}")



@rr_bot.message_handler(commands=['restart'])
def who_duty_today(message):
    try:
        bot_functions.check_permission(message, users)
        rr_bot.reply_to(message, f"Бот перезапущен - {datetime.datetime.now()}")
        subprocess.Popen(['./start.sh'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    except:
        rr_bot.send_message(exc.args[1], exc.args[0])


if __name__ == '__main__':
    try:
        rr_bot.send_message("1739060486", f"бот перезапущен - {datetime.datetime.now()}")
        rr_bot.polling(none_stop=True, interval=0, timeout=20)
    except Exception as exc:
        rr_bot.send_message("1739060486", f'{exc[1]}')
        subprocess.Popen(['./start.sh'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
