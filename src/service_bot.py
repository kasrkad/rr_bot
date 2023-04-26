from os import environ, makedirs
from multiprocessing import Queue
from threading import excepthook

makedirs('logs',exist_ok=True)

try:
    control_queue = Queue(-1)
    from ess_bot.service_bot.bot_module import Ess_service_bot
    from ess_bot.notify_module.notify_lib import Notifyer
    from ess_bot.hpsm_module.hpsm_checker import Hpsm_checker 
    TG_BOT_TOKEN = environ['TG_BOT_TOKEN']


    checker = Hpsm_checker(bot_token=TG_BOT_TOKEN,rr_file_path='./rr_list.txt',request_codes_file_path='./request_codes.txt',
                           control_queue=control_queue, daemon=True)

    bot = Ess_service_bot(bot_token = TG_BOT_TOKEN, hpsm_control_queue=control_queue)
    noty = Notifyer(bot_token=TG_BOT_TOKEN, daemon=True)
except Exception as exc:
    print(exc, exc.args)
    exit(1)
    
def main():
    noty.start()
    checker.start()
    while True:
        try:
            bot.run()
        except Exception as exc:
            print(exc, exc.args)
            continue


if __name__ == '__main__':
    main()
