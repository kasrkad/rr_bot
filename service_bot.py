import os
os.makedirs('logs',exist_ok=True)
from service_bot.bot_module import Ess_service_bot
from config import *
from notify_module.notify_lib import *
from hpsm_module.hpsm_checker import Hpsm_checker

bot = Ess_service_bot(bot_token = TG_BOT_TOKEN )
bot.initilize(path_to_admin_json='./basic_settings/admins.json',path_to_notify_json='./basic_settings/notifys.json')



noty = Notifyer(bot_token=TG_BOT_TOKEN, daemon=True)
noty.start()
bot.run()
