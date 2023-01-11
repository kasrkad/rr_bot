from config import *
from hpsm_module.hpsm_checker import Hpsm_checker

checker = Hpsm_checker(bot_token=TG_BOT_TOKEN,rr_file_path='./rr_list.txt')
checker.start()
