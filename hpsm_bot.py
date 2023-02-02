from os import environ
from ess_bot.hpsm_module.hpsm_checker import Hpsm_checker
TG_BOT_TOKEN = environ["TG_BOT_TOKEN"]

checker = Hpsm_checker(bot_token=TG_BOT_TOKEN,rr_file_path='./rr_list.txt',request_codes_file_path='./request_codes.txt')
checker.start()
