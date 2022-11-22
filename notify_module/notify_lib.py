import sys
sys.path.append('../')
from sqlite_module.sql_lib import get_all_notifys,create_tables,change_notify_status,midnight_reset_notifications


class Notify:
    def __init__(self,bd_name, time, work_day,text, status ):
        self._time = time
        self._text = text
        self._work_day = work_day
        self._bd_name = bd_name
        self._status = status

    def __str__(self):
        return (f'time = {self._time}, bd_name = {self._bd_name}, text = {self._text}')


class Notifyer:
    def __init__(self):
        self.notifycations = []

    def check_for_notify(self, obj):
        from datetime import datetime
        current_hour = datetime.now().strftime("%H")
        current_min = datetime.now().strftime("%M")
        notify_hours, notify_min = obj._time.strip().split('-')
        current_work_day =  datetime.today().weekday()
        notify_start_day, notify_end_day = obj._work_day.split('-')
        notify_work_days = [day for day in range(int(notify_start_day)-1,int(notify_end_day))]
        if current_hour == notify_hours and current_min == notify_min and obj._status == '0' and current_work_day in notify_work_days:
            print(obj)
            obj._status = '1'
            change_notify_status(obj._bd_name)
            print(f'{obj._bd_name} done? {obj._status}')
        else :
            print("Не о чем уведомлять")

    def load_all_notyfications(self):
        all_notifys = get_all_notifys()
        for notify_data in all_notifys:
            self.notifycations.append(Notify(*notify_data))

    def run(self):
        from time import sleep
        self.load_all_notyfications()
        while True:
            for _n in self.notifycations:
                print(_n._bd_name)
                self.check_for_notify(_n)
            sleep(20)
    


def main():
    notifyer = Notifyer()
    midnight_reset_notifications()
    notifyer.run()


if __name__=='__main__':
    main()

# notify1 = Notify('16-25', 'not text', '0-5', 'not_bame_bd')


# notifyer = Notifyer(notify1)
# notifyer.run()