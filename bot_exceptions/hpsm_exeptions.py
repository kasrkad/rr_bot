class GetHpsmFrameException(Exception):

    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        if self.message:
            return f'GetHpsmFrameException, {self.message}'
        else:

            return 'GetHpsmFrameException has been raised'


class GetPageException(Exception):

    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        if self.message:
            return f'GetPageException, {self.message}'
        else:

            return 'GetPageExeption has been raised'


class HpsmLoginException(Exception):

    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        if self.message:
            return f'HpsmLoginException, {self.message}'
        else:
            return 'HpsmLoginException has been raised'

class EmptyRequestsListReturn(Exception):

    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        if self.message:
            return f'EmptyRequestsListReturn, {self.message}'
        else:
            return 'EmptyRequestsListReturn has been raised'