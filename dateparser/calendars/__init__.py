class CalendarBase(object):

    def __init__(self, source):
        self.source = source

    def get_date(self):
        raise NotImplemented
