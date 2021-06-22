#!/bin/python3

import telebot
import config
import json



rr_bot = telebot.TeleBot(config.BOT_TOKEN, parse_mode='MARKDOWN')



@rr_bot.message_handler(commands=['help'])
def print_help(message):
	rr_bot.reply_to(message,"Пока я умею /дежурю(Дежурю) - регистрация дежурного, /дежурный(Дежурный) - скажу кто сейчас дежурный ")


@rr_bot.message_handler(commands=['дежурю','Дежурю'])
def get_duty_id(message):
	rr_bot.reply_to(message,f'Дежурный зарегистрирован - {message.from_user.first_name} {message.from_user.last_name}')
	global duty_eng 
	duty_eng = {"t_id":message.from_user.id, "first_name":message.from_user.first_name, "last_name":message.from_user.last_name}
	with open ('duty.json','w',encoding='utf8') as duty_file:
		json.dump(duty_eng,duty_file, ensure_ascii=False)

@rr_bot.message_handler(commands=['дежурный','Дежурный'])
def who_duty_today(message):
	global duty_eng 
	duty_eng = {}
	if duty_eng:
		rr_bot.reply_to(message,f"Сегодня дежурит [{duty_eng['first_name']} {duty_eng['last_name']}](tg://user?id={duty_eng['t_id']})")
	else:
		with open ('duty.json', 'r', encoding='utf8') as duty_file:
			duty_eng = json.load(duty_file)
		rr_bot.reply_to(message,f"Сегодня дежурит [{duty_eng['first_name']} {duty_eng['last_name']}](tg://user?id={duty_eng['t_id']})")

rr_bot.polling(none_stop=True, interval=0)