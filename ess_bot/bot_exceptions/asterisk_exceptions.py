class FailToChangeDutyPhone(Exception):

    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        if self.message:
            return f'FailToChangeDutyPhone, {self.message}'
        else:
            return 'FailToChangeDutyPhone has been raised'


class FailAcceptNewDutyPhone(Exception):

    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        if self.message:
            return f'FailAcceptNewDutyPhone, {self.message}'
        else:
            return 'FailAcceptNewDutyPhone has been raised'