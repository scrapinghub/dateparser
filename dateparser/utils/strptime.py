import imp

def strptime():
    """Monkey patching _strptime to avoid problems related with non-english
    locale changes on the system.

    For example, if system's locale is set to fr_FR. Parser won't recognize
    any date since all languages are translated to english dates.
    """

    strptime = imp.load_module(
        'strptime_patched', *imp.find_module('_strptime')
    )

    strptime._getlang = lambda: ('en_US', 'UTF-8')
    strptime.calendar.day_abbr = [
        'mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'
    ]
    strptime.calendar.day_name = [
        'monday', 'tuesday', 'wednesday', 'thursday',
        'friday', 'saturday', 'sunday'
    ]
    strptime.calendar.month_abbr = [
        '', 'jan', 'feb', 'mar', 'apr', 'may', 'jun',
        'jul', 'aug', 'sep', 'oct', 'nov', 'dec'
    ]
    strptime.calendar.month_full = [
        '', 'january', 'february', 'march', 'april',
        'may', 'june', 'july', 'august', 'september',
        'october', 'november', 'december'
    ]

    return strptime._strptime_time

__strptime = strptime()
