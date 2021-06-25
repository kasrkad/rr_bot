#!/bin/python3
import os
import telebot
import config
import json
from bot_functions import check_duty_eng, get_document

rr_bot = telebot.TeleBot(config.BOT_TOKEN, parse_mode='MARKDOWN')

global duty_eng
duty_eng = check_duty_eng()

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

@rr_bot.message_handler(commands=['КтоДежурит','ктодежурит'])
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
