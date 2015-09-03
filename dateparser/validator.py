# coding: utf-8
import regex


ATTR_GETTER = regex.compile('\{([a-z_]+)\}')


class DateValidator(object):

    _regex_cache = []

    _re_delimiter = {
        'delimiters': [',', '-', '/', '\\', '.'],
        're': r'(?P<delimiter>(?:\L<delimiters>)+|\s+)'
    }

    _re_month_names = {
        'months': ['january', 'february', 'march', 'april', 'may',
                   'june', 'july', 'august', 'september', 'november', 'december',
                   'jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul',
                   'aug', 'sep', 'oct', 'nov', 'dec',],
        're': r'(?P<month>\L<months>)'
    }

    _re_day_names = {
        'days': ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday',
                 'mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'],
        're': r'(?P<dayname>\L<daynames>)'
    }

    _re_year = {'re': r'(?P<year>(?:\s|\b)(?:\d{2}|\d{4})(?:\s|\b))'}
    _re_month = {'re': r'(?P<month>(?:\s|\b)(?:0?[1-9]|1[0-2])(?:\s|\b))'}
    _re_day = {'re': r'(?P<day>(?:\s|\b)(?:[1-9]|[0-2][0-9]|3[0-1])(?:\s|\b))'}

    _re_hour = {'re': r'(?P<hour>(?:\s|\b)(?:2[0-3]|[0-1]?[0-9])(?:\s|\b))'}
    _re_twelve_hour = {'re': r'(?P<twelvehour>0?[0-9]|1[0-2])'}
    _re_minute = {'re': r'(?::(?P<minute>(?:\s|\b)(?:[0-5]?[0-9])(?:\s|\b)))?'}
    _re_second = {'re': r'(?::(?P<second>(?:[0-5]?[0-9]|60)(?:\s|\b)?))?'}
    _re_time = {'re': r'%s%s%s' % (_re_hour['re'], _re_minute['re'], _re_second['re'])}
    _re_period = {'re': r'(?P<period>\.?[ap.]{1,2}m\.?)'}
    _re_twelve_hour_time = {
        're': r'%s%s%s\s*%s' % (
            _re_twelve_hour['re'],
            _re_minute['re'],
            _re_second['re'],
            _re_period['re'])
    }

    _re_utc_offset = {
        're': (r'(?:(?P<sign>[-−])(?P<utchour>(?:0[0-9]|1[0-2])):?(?P<utcminute>[03]0)'
                '|'
                '(?P<sign>[+])(?P<utchour>(?:0[0-9]|1[0-4])):?(?P<utcminute>[034][05])'
                '|'
                '(?P<sign>[+-]?)(?P<utchour>00):?(?P<utcminute>00))')
    }

    _re_abbreviated_tz = {'re': r'(?P<tz>[A-Z]{3,4}|Z)'}

    date_formats = [
        # word formats
        r'{year}{delimiter}{month_names}{delimiter}{day}\s*{twelve_hour_time}\W*{abbreviated_tz}',
        r'{year}{delimiter}{month_names}{delimiter}{day}\s*{twelve_hour_time}\W*{utc_offset}',
        r'{year}{delimiter}{month_names}{delimiter}{day}\s*{time}\W*{abbreviated_tz}',
        r'{year}{delimiter}{month_names}{delimiter}{day}\s*{time}\W*{utc_offset}',
        r'{year}{delimiter}{month_names}{delimiter}{day}\s*{twelve_hour_time}',
        r'{year}{delimiter}{month_names}{delimiter}{day}\s*{time}',
        r'{year}{delimiter}{month_names}{delimiter}{day}',

        r'{year}{delimiter}{day}{delimiter}{month_names}\s*{twelve_hour_time}\W*{abbreviated_tz}',  # test covered
        r'{year}{delimiter}{day}{delimiter}{month_names}\s*{twelve_hour_time}\W*{utc_offset}',  # test covered
        r'{year}{delimiter}{day}{delimiter}{month_names}\s*{time}\W*{abbreviated_tz}',  # test covered
        r'{year}{delimiter}{day}{delimiter}{month_names}\s*{time}\W*{utc_offset}',  # test covered
        r'{year}{delimiter}{day}{delimiter}{month_names}\s*{twelve_hour_time}',  # test covered
        r'{year}{delimiter}{day}{delimiter}{month_names}\s*{time}',  # test covered
        r'{year}{delimiter}{day}{delimiter}{month_names}',  # test covered

        r'{month_names}{delimiter}{day}{delimiter}{year}\s*{twelve_hour_time}\W*{abbreviated_tz}',  # test covered
        r'{month_names}{delimiter}{day}{delimiter}{year}\s*{twelve_hour_time}\W*{utc_offset}',  # test covered
        r'{month_names}{delimiter}{day}{delimiter}{year}\s*{time}\W*{abbreviated_tz}',  # test covered
        r'{month_names}{delimiter}{day}{delimiter}{year}\s*{time}\W*{utc_offset}',  # test covered
        r'{month_names}{delimiter}{day}{delimiter}{year}\s*{twelve_hour_time}',  # test covered
        r'{month_names}{delimiter}{day}{delimiter}{year}\s*{time}',  # test covered
        r'{month_names}{delimiter}{day}{delimiter}{year}',  # test covered

        r'{month_names}{delimiter}{year}{delimiter}{day}\s*{twelve_hour_time}\W*{abbreviated_tz}',  # test covered
        r'{month_names}{delimiter}{year}{delimiter}{day}\s*{twelve_hour_time}\W*{utc_offset}',  # test covered
        r'{month_names}{delimiter}{year}{delimiter}{day}\s*{time}\W*{abbreviated_tz}',  # test covered
        r'{month_names}{delimiter}{year}{delimiter}{day}\s*{time}\W*{utc_offset}',  # test covered
        r'{month_names}{delimiter}{year}{delimiter}{day}\s*{twelve_hour_time}',  # test covered
        r'{month_names}{delimiter}{year}{delimiter}{day}\s*{time}',  # test covered
        r'{month_names}{delimiter}{year}{delimiter}{day}',  # test covered

        r'{day}{delimiter}{year}{delimiter}{month_names}\s*{twelve_hour_time}\W*{abbreviated_tz}',  # test covered
        r'{day}{delimiter}{year}{delimiter}{month_names}\s*{twelve_hour_time}\W*{utc_offset}',  # test covered
        r'{day}{delimiter}{year}{delimiter}{month_names}\s*{time}\W*{abbreviated_tz}',  # test covered
        r'{day}{delimiter}{year}{delimiter}{month_names}\s*{time}\W*{utc_offset}',  # test covered
        r'{day}{delimiter}{year}{delimiter}{month_names}\s*{twelve_hour_time}',  # test covered
        r'{day}{delimiter}{year}{delimiter}{month_names}\s*{time}',  # test covered
        r'{day}{delimiter}{year}{delimiter}{month_names}',  # test covered

        r'{day}{delimiter}{month_names}{delimiter}{year}\s*{twelve_hour_time}\W*{abbreviated_tz}',  # test covered
        r'{day}{delimiter}{month_names}{delimiter}{year}\s*{twelve_hour_time}\W*{utc_offset}',  # test covered
        r'{day}{delimiter}{month_names}{delimiter}{year}\s*{time}\W*{abbreviated_tz}',  # test covered
        r'{day}{delimiter}{month_names}{delimiter}{year}\s*{time}\W*{utc_offset}',  # test covered
        r'{day}{delimiter}{month_names}{delimiter}{year}\s*{twelve_hour_time}',  # test covered
        r'{day}{delimiter}{month_names}{delimiter}{year}\s*{time}',  # test covered
        r'{day}{delimiter}{month_names}{delimiter}{year}',  # test covered

        # numeric formats
        r'{year}{delimiter}{month}{delimiter}{day}\s*{twelve_hour_time}\W*{abbreviated_tz}',
        r'{year}{delimiter}{month}{delimiter}{day}\s*{twelve_hour_time}\W*{utc_offset}',
        r'{year}{delimiter}{month}{delimiter}{day}\s*{time}\W*{abbreviated_tz}',
        r'{year}{delimiter}{month}{delimiter}{day}\s*{time}\W*{utc_offset}',
        r'{year}{delimiter}{month}{delimiter}{day}\s*{twelve_hour_time}',
        r'{year}{delimiter}{month}{delimiter}{day}\s*{time}',
        r'{year}{delimiter}{month}{delimiter}{day}',

        r'{year}{delimiter}{day}{delimiter}{month}\s*{twelve_hour_time}\W*{abbreviated_tz}',  # test covered
        r'{year}{delimiter}{day}{delimiter}{month}\s*{twelve_hour_time}\W*{utc_offset}',  # test covered
        r'{year}{delimiter}{day}{delimiter}{month}\s*{time}\W*{abbreviated_tz}',  # test covered
        r'{year}{delimiter}{day}{delimiter}{month}\s*{time}\W*{utc_offset}',  # test covered
        r'{year}{delimiter}{day}{delimiter}{month}\s*{twelve_hour_time}',  # test covered
        r'{year}{delimiter}{day}{delimiter}{month}\s*{time}',  # test covered
        r'{year}{delimiter}{day}{delimiter}{month}',  # test covered

        r'{month}{delimiter}{day}{delimiter}{year}\s*{twelve_hour_time}\W*{abbreviated_tz}',  # test covered
        r'{month}{delimiter}{day}{delimiter}{year}\s*{twelve_hour_time}\W*{utc_offset}',  # test covered
        r'{month}{delimiter}{day}{delimiter}{year}\s*{time}\W*{abbreviated_tz}',  # test covered
        r'{month}{delimiter}{day}{delimiter}{year}\s*{time}\W*{utc_offset}',  # test covered
        r'{month}{delimiter}{day}{delimiter}{year}\s*{twelve_hour_time}',  # test covered
        r'{month}{delimiter}{day}{delimiter}{year}\s*{time}',  # test covered
        r'{month}{delimiter}{day}{delimiter}{year}',  # test covered

        r'{month}{delimiter}{year}{delimiter}{day}\s*{twelve_hour_time}\W*{abbreviated_tz}',  # test covered
        r'{month}{delimiter}{year}{delimiter}{day}\s*{twelve_hour_time}\W*{utc_offset}',  # test covered
        r'{month}{delimiter}{year}{delimiter}{day}\s*{time}\W*{abbreviated_tz}',  # test covered
        r'{month}{delimiter}{year}{delimiter}{day}\s*{time}\W*{utc_offset}',  # test covered
        r'{month}{delimiter}{year}{delimiter}{day}\s*{twelve_hour_time}',  # test covered
        r'{month}{delimiter}{year}{delimiter}{day}\s*{time}',  # test covered
        r'{month}{delimiter}{year}{delimiter}{day}',  # test covered

        r'{day}{delimiter}{year}{delimiter}{month}\s*{twelve_hour_time}\W*{abbreviated_tz}',  # test covered
        r'{day}{delimiter}{year}{delimiter}{month}\s*{twelve_hour_time}\W*{utc_offset}',  # test covered
        r'{day}{delimiter}{year}{delimiter}{month}\s*{time}\W*{abbreviated_tz}',  # test covered
        r'{day}{delimiter}{year}{delimiter}{month}\s*{time}\W*{utc_offset}',  # test covered
        r'{day}{delimiter}{year}{delimiter}{month}\s*{twelve_hour_time}',  # test covered
        r'{day}{delimiter}{year}{delimiter}{month}\s*{time}',  # test covered
        r'{day}{delimiter}{year}{delimiter}{month}',  # test covered

        r'{day}{delimiter}{month}{delimiter}{year}\s*{twelve_hour_time}\W*{abbreviated_tz}',  # test covered
        r'{day}{delimiter}{month}{delimiter}{year}\s*{twelve_hour_time}\W*{utc_offset}',  # test covered
        r'{day}{delimiter}{month}{delimiter}{year}\s*{time}\W*{abbreviated_tz}',  # test covered
        r'{day}{delimiter}{month}{delimiter}{year}\s*{time}\W*{utc_offset}',  # test covered
        r'{day}{delimiter}{month}{delimiter}{year}\s*{twelve_hour_time}',  # test covered
        r'{day}{delimiter}{month}{delimiter}{year}\s*{time}',  # test covered
        r'{day}{delimiter}{month}{delimiter}{year}',  # test covered
    ]

    def __init__(self, date_string):
        self.date_string = date_string

    def populate_regex_cache(self):
        cache_entry = []

        for pattern in self.date_formats:
            keywords = {}
            compile_keywords = {}
            for keyword in ATTR_GETTER.findall(pattern):
                attr_dict  = getattr(self, '_re_%s' % keyword).copy()
                keywords[keyword] = attr_dict.pop('re')
                compile_keywords.update(attr_dict)

            raw_pattern = pattern.format(**keywords)
            compiled_pattern = regex.compile(
                raw_pattern,
                flags=regex.V1 | regex.DOTALL | regex.I,
                **compile_keywords)

            cache_entry.append(compiled_pattern)

        self._regex_cache = cache_entry
        
    def validate(self):
        results = []

        length_not_visited = len(self.date_string)
        start_index = 0

        if not self._regex_cache:
            self.populate_regex_cache()

        while length_not_visited > 0:
            for re_obj in self._regex_cache:
                match = re_obj.match(self.date_string[start_index:])
                if match:
                    length_not_visited -= match.span()[-1]
                    start_index += match.span()[-1]
                    results.append(match.capturesdict())
                    break
            else:
                length_not_visited = 0

        return results
