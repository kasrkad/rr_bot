#!/bin/python3
from subprocess import Popen, PIPE
import datetime
from config import *
import glob
import os
import shutil
import re
import json

class Cct_message_handler_loader:


	def __init__(self,bot):
		self.bot=bot
		self.load_settings = {}
		self.dump_settings = {}
		self.message_with_target_stand = None
		self.message_with_source_stand = None
		self.message_with_artifacts = None
		self.message_with_commits = None

	
	def remove_files(self,list):
		for file in list:
			os.remove(file)

	def validate_stand(self, stand_message):
		if stand_message.text.strip().lower() not in list(stand_list.keys()):
			self.bot.reply_to(stand_message,f"Этого стенда {stand_message.text} нет в списке доступных ")
			return False
		return f"{stand_message.text.strip().lower()}"

	def validate_commit(self, commit_message):
		commit = commit_message.text.strip()
		if len(commit) > 6  and re.match(r'[a-z0-9]{7,9}', commit.lower()):
			return commit.lower()
		self.bot.reply_to(commit_message, f"Некорректный коммит {commit_message.text}")
		return False   


	def validate_task(self,task_message):
		cct, artifacts = task_message.text.strip().replace(' ','').split(';')
		cct = cct.split(',')
		artifacts = artifacts.split(',')
		artifacts_for_check = set(artifacts)
		cct_for_check = set(cct)
		for artifact in artifacts_for_check:
			if artifact.strip().lower() not in CORRECT_ARTIFACTS:
				self.bot.reply_to(task_message,f'Нeкорректные данные в списке артефактов {artifact}')
				return False
		for ccts in cct_for_check:
			if len(str(ccts)) > 5:
				self.bot.reply_to(task_message,f'Нeкорректные данные CCT {cct_for_check}')
				return False

		return f'{",".join(ccts.strip() for ccts in cct_for_check)};{",".join(x.strip().lower() for x in artifacts_for_check)}'


	def abort_cct(self, message):
		if message.text.lower() == "отмена":
			return True


	def end_conversation(self, message):
		self.bot.reply_to(message,"Операция отменена.")
		return

	def target_stand_set(self, message):
		if self.abort_cct(message):
			self.end_conversation(message)
		else:
			msg = self.bot.reply_to(message, f"""Введите целевой стенд, доступные стенды:
	{', '.join(k for k in stand_list.keys())}""")
			self.bot.register_next_step_handler(msg, self.cct_enter_step)


	def cct_enter_step(self,message):
		if self.abort_cct(message):
			self.end_conversation(message)
		else:
			if self.validate_stand(message):
				self.message_with_target_stand = message
				self.load_settings["eng_id"] = message.from_user.id
				self.load_settings["stand"] = message.text.strip().lower()
				msg = self.bot.reply_to(message, "Введите task simicli.\n Пример: 78751,78634;cct,vis")
				self.bot.register_next_step_handler(msg, self.artifact_enter_step)
			else:
				self.target_stand_set(message)


	def artifact_enter_step(self,message):
		try:
			if self.abort_cct(message):
				self.end_conversation(message)
			else:
				if self.validate_task(message):
					self.load_settings["task"] = self.validate_task(message)
					self.message_with_artifacts = message
					msg = self.bot.reply_to(message, "Введите коммит: \nПример: 81dsf93")
					self.bot.register_next_step_handler(msg, self.simi_cli_check_and_start)
				else:
					self.cct_enter_step(self.message_with_target_stand)
		except Exception as exc:
			self.bot.reply_to(message,f"Некорректные данные {exc.args}")
			self.cct_enter_step(self.message_with_target_stand)

	def simi_cli_check_and_start(self,message):
		if self.abort_cct(message):
			self.end_conversation(message)
		else:
			if self.validate_commit(message):
				self.load_settings['commit'] = self.validate_commit(message)
				msg = self.bot.reply_to(message, f"Проверьте настройки для simicli,\nСтенд :{self.load_settings['stand']}, Артефакты: {self.load_settings['task']}, Коммит: {self.load_settings['commit']} ,\nЕсли все корректно, введите Y")
				self.bot.register_next_step_handler(msg, self.start_cli)
			else:
				self.artifact_enter_step(self.message_with_artifacts)


	def start_cli(self,message):
		answer = message.text
		print(self.load_settings)
		if answer.strip() == 'Y':
			self.bot.send_message(message.chat.id, f"Стартуем simicli с параметрами: applycommit Стенд :{self.load_settings['stand']}, Артефакты: {self.load_settings['task']}, Коммит: {self.load_settings['commit']}")
			try:
				loader = Artifact(**self.load_settings)
				loader.load_artifact()
				self.bot.send_message(message.from_user.id,"Загрузка успешно завершена")
			except OSError as exc:
				print(exc)
				self.bot.send_message(message.from_user.id,f"Возникли ошибки {exc}")
				error_logs = glob.glob('./logs/*error.txt')
				for error_log in error_logs:
					send_error = open(error_log)
					self.bot.send_document(message.from_user.id,send_error)
				self.remove_files(glob.glob('./logs/*'))
			except ValueError as exc:
				raise ValueError(exc)
		else:
			self.bot.send_message(message.chat.id, "Запуск отменен, переделывай.")


class Cct_message_hander_mover(Cct_message_handler_loader):


	def source_stand_set(self,message):  
		msg = self.bot.reply_to(message, f"""Введите стенд источник, доступные стенды:
{', '.join(k for k in stand_list.keys())}""")
		self.bot.register_next_step_handler(msg, self.target_stand_set)

	def target_stand_set(self,message):
		if self.abort_cct(message):
			self.end_conversation(message)
		else:
			if self.validate_stand(message):
				self.message_with_source_stand = message  
				self.dump_settings['stand'] = self.validate_stand(message)	
				msg = self.bot.reply_to(message, f"""Введите целевой стенд, доступные стенды:
			{', '.join(k for k in stand_list.keys())}""")
				self.bot.register_next_step_handler(msg, self.cct_enter_step)
			else:
				self.source_stand_set(message)



	def cct_enter_step(self,message):
		if self.abort_cct(message):
			self.end_conversation(message)
		else:
			if self.validate_stand(message):
				self.message_with_target_stand = message
				self.load_settings["stand"] = self.validate_stand(message)
				msg = self.bot.reply_to(message, "Введите task simicli.\n Пример: 78751,78634;cct,vis")
				self.bot.register_next_step_handler(msg, self.artifact_enter_step)
			else:
				self.target_stand(message)

	def artifact_enter_step(self,message):
		if self.abort_cct(message):
			self.end_conversation(message)
		else:
			if self.validate_task(message):
				self.message_with_artifacts = message
				self.load_settings["task"] = self.validate_task(message)
				self.dump_settings["task"] = self.validate_task(message)
				msg = self.bot.reply_to(message, f"Проверка задачи стенд источник- {self.dump_settings['stand']}, целевой стенд- {self.load_settings['stand']}, артефакты {self.load_settings['task']} Введите Y для продолжения.")
				self.bot.register_next_step_handler(msg, self.start_cli)	
			else:
				self.cct_enter_step(message)


	def start_cli(self,message):
		answer = message.text
		if answer.strip() == 'Y':
			try:
				self.bot.send_message(message.from_user.id, f"Забираем артефакты со стенда {self.dump_settings['stand']}")
				print(f"source stand {self.dump_settings}")
				print(f"target stand {self.load_settings}")
				dumper = Artifact(**self.dump_settings)
				dumper.dump_artifact()
				self.bot.send_message(message.from_user.id, f"Артефакты скачаны начинаем загрузку на стенд {self.load_settings['stand']}")
				loader = Artifact(**self.load_settings)
				loader.load_artifact()
				self.bot.send_message(message.from_user.id,"Загрузка успешно завершена")
			except OSError as exc:
				self.bot.send_message(message.from_user.id,"Возникли ошибки")
				print(exc)
				error_logs = glob.glob('./logs/*error.txt')
				for error_log in error_logs:
					send_error = open(error_log)
					self.bot.send_document(message.from_user.id,send_error)
				self.remove_files(glob.glob('./logs/*'))
		else:
			self.bot.send_message(message.chat.id, "Запуск отменен, переделывай.")



class Artifact:


	def __init__(self, stand=None, task=None, commit=None, eng_id = None):
		self.stand=stand
		self.task=task
		self.commit=commit
		self.eng_id = eng_id
		self.cct_folder = './cct/cct_dump'

	def remove_files(self, log_files):
		for file in log_files:
			os.remove(file)

	def remove_folders(self):
		dirs_for_remove = glob.glob(f'{self.cct_folder}/*')
		for dir in dirs_for_remove:
			shutil.rmtree(dir)

	def print_params(self):
		return f"{self.stand}, {self.task}, {self.commit}"


	def add_params(self,**kwargs):
		self.task=kwargs.get('task')
		self.commit=kwargs.get('commit')


	def write_activity_log(self, action):
		with open("./cct/cct_logs/activity.json", 'a', encoding='utf8') as activity_file:
			json.dump({"time": datetime.datetime.today().strftime("%d-%m-%Y"),"engeneer_tg_id": self.eng_id, "stand":self.stand, "action":action ,"task":self.task}, activity_file,ensure_ascii=False)
			activity_file.write("\n")


	def settings_loader(self):
		if self.stand in stand_list.keys():
			return stand_list[self.stand]
		raise ValueError


	def error_checker(self):
		error_file = glob.glob('./logs/*error.txt')
		if os.path.getsize(error_file[0]) == 0:
			return
		raise OSError("Ошибки в логах")


	def load_artifact(self):
		load_from_commit  = [f'--task {self.task}',
				f'--repository-changeset {self.commit}',
				'--checkout',
				f'--repository-dir {SIMI_DOC_REPO_FOLDER}',
				'--fetch ',
				f'--repository-url {SIMI_DOC_REPO_URL}',
				f'--repository-username {SIMI_DOC_REPO_USER}',
				f'--repository-password {SIMI_DOC_REPO_PASS}']

		load_from_folder = [f'--task {self.task}', f'--dump {self.cct_folder}']
		for stand_name, stand_settings in self.settings_loader().items():
			if self.commit:
				stand_set = ['apply'] + stand_settings + load_from_commit
			else:
				stand_set = ['apply'] + stand_settings + load_from_folder
			process = Popen(['bash','./simi_cli_run.sh'," ".join(arg for arg in stand_set)], stdout=PIPE, stderr=PIPE)
			err, out = process.communicate()
			process.wait()			
			print(out.decode('utf8'))
			self.error_checker()
			self.remove_files(glob.glob('./logs/*'))
		self.remove_folders()
		self.write_activity_log("load")

	def dump_artifact(self):
		dump_settings = [f'--task {self.task}', f'--dump {self.cct_folder}']
		for stand_name, stand_settings in self.settings_loader().items():
			stand_set = ['dump'] + stand_settings + dump_settings
			break
		print(stand_set)
		process = Popen(['bash','./simi_cli_run.sh'," ".join(arg for arg in stand_set)], stdout=PIPE, stderr=PIPE)
		err, out = process.communicate()
		process.wait()			
		print(out.decode('utf8'))
		self.error_checker()
		self.write_activity_log("dump")
		self.remove_files(glob.glob('./logs/*'))


