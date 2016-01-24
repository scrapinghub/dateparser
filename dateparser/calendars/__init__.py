class CalendarBase(object):
    """Base setup class for non-Gregorian calendar system.

    :param source:
        Date string passed to calendar parser.
    :type source: str|unicode
    """

    def __init__(self, source):
        self.source = source

    def get_date(self):
        raise NotImplemented
