#!/bin/python3
import os
import subprocess
import telebot
import config
import json
from bot_functions import check_duty_eng, get_document, remove_files
import glob

rr_bot = telebot.TeleBot(config.BOT_TOKEN, parse_mode='MARKDOWN')

global duty_eng
duty_eng = check_duty_eng()

@rr_bot.message_handler(commands=['в_приоритете'])
def artifact_download_dev(message): # грузит только на дев и только с коммита
    msg = rr_bot.reply_to(message,"введите ссt")
    rr_bot.register_next_step_handler(msg,cct_enter_step)

def cct_enter_step(message):
    try:
        cct = message.text
        with open('./simi_cli/ids', 'w', encoding='utf8') as enter_cct_file:
           enter_cct_file.write(f"{cct}; ")
        print (cct)
        msg = rr_bot.reply_to(message,"введите параметры загрузки артефактов в формате simi-cli : cct, vis, tmpl.\n Пример: cct, vis ")
        rr_bot.register_next_step_handler(msg,artifact_enter_step)
    except Exception as exc:
        rr_bot.reply_to(message,f"Что то пошло не так,{exc}")

def artifact_enter_step(message):
    artifacts = message.text
    print(artifacts)
    with open('./simi_cli/ids', 'a', encoding='utf8') as enter_artifacts_file:
        enter_artifacts_file.write(artifacts)
    msg = rr_bot.reply_to(message,"Введите коммит: \nПример: 81dsf93")
    rr_bot.register_next_step_handler(msg,simi_cli_check_and_start)

def simi_cli_check_and_start(message):
    global commit
    commit = message.text
    print(commit)
    with open ('./simi_cli/ids','r', encoding='utf8') as check_ids_file:
        simi_cli_ids = check_ids_file.readline()
    print (f"Проверьте настройки для simi_cli\n ids {simi_cli_ids},\n commit {commit}")
    msg = rr_bot.reply_to(message,f"Проверьте настройки для simicli,\nДля загрузки: {simi_cli_ids},\nCommit: {commit}\nЕсли все корректно, введите Y")
    rr_bot.register_next_step_handler(msg,start_cli)

def start_cli(message):
    answer = message.text
    if answer.strip() == 'Y':
        rr_bot.send_message(message.chat.id,f"Стартуем simicli с параметрами: applycommit dev {commit}")
        out = subprocess.Popen(['./simi_cli/artifact.sh','applycommit','dev', commit], stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        out.wait()
        logs_for_send = glob.glob('./logs/*log.txt')
        rr_bot.send_message(message.chat.id,"Лови логи")
        for files in logs_for_send:
            doc = open(files)
            rr_bot.send_document(message.from_user.id,doc)
        remove_files(glob.glob("./logs/*"))
    else:
        rr_bot.send_message(message.chat.id,"Запуск отменен, переделывай.")

@rr_bot.message_handler(commands=['скачай'])
def download_document(message):
    download_list = message.text.split(" ")
    for doc in download_list[1:]:
        with open('./doc_download_log/log.txt', 'a', encoding='utf8') as doc_log:
            doc_log.write(f"{doc} скачан пользователем {message.from_user.first_name} {message.from_user.last_name} - id {message.from_user.id}\n")
        print(message.from_user.id)
        get_document(doc,message.from_user.id)
        document = open(f'./documents_output/{doc}.xml')
        rr_bot.send_document(message.from_user.id, document)
        os.remove(f'./documents_output/{doc}.xml')

@rr_bot.message_handler(commands=['help'])
def print_help(message):
    rr_bot.reply_to(message," Владею нюндзюцу:\n /help : выведу это сообщение,\n /дежурю или /дежурный : регистрирую как дежурного инженера,\n /ктоДежурит: укажу на дежурного инженера,\n /скачай docID : скачаю с ППАК документ и отправлю в личку.", parse_mode="MARKDOWN")

@rr_bot.message_handler(commands=['дежурю','Дежурю', 'Дежурный', 'дежурный'])
def get_duty_id(message):
    global duty_eng
    rr_bot.reply_to(message,f'Дежурный зарегистрирован - {message.from_user.first_name} {message.from_user.last_name}')
    duty_eng = {"t_id":message.from_user.id, "first_name":message.from_user.first_name, "last_name":message.from_user.last_name}
    with open ('duty.json','w',encoding='utf8') as duty_file:
        json.dump(duty_eng,duty_file, ensure_ascii=False)

@rr_bot.message_handler(commands=['КтоДежурит','ктодежурит','ктоДежурит'])
def who_duty_today(message):
    global duty_eng
    if duty_eng:
        rr_bot.reply_to(message,f"Сегодня дежурит [{duty_eng['first_name']} {duty_eng['last_name']}](tg://user?id={duty_eng['t_id']})")
    else:
        rr_bot.reply_to(message,f"Дежурный не обнаружен, вызываем ответственного: [Александр Бауман](tg://user?id=753785354)")

if __name__=='__main__':

	try:
		rr_bot.polling(none_stop=True, interval=0, timeout=20)
	except Exception as exc:
		with open ('bot_exc.txt', 'a', encoding='utf8') as exc_file:
			exc_file.write(str(exc) + "\n")
