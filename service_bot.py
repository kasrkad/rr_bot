from os import environ, makedirs

makedirs('logs',exist_ok=True)

try:
    from ess_bot.service_bot.bot_module import Ess_service_bot
    from ess_bot.notify_module.notify_lib import Notifyer


    TG_BOT_TOKEN = environ['TG_BOT_TOKEN']
    bot = Ess_service_bot(bot_token = TG_BOT_TOKEN )
    bot.initilize(path_to_admin_json='./basic_settings/admins.json',path_to_notify_json='./basic_settings/notifys.json')
    noty = Notifyer(bot_token=TG_BOT_TOKEN, daemon=True)
    noty.start()
    bot.run()
    
except Exception as exc:
    print(exc, exc.args)