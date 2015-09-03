# coding: utf-8
import regex


ATTR_GETTER = regex.compile('\{([a-z_]+)\}')


class DateValidator(object):

    _formats_regex_cache = []

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
        're': r'(?P<dayname>\L<days>)'
    }

    _re_parts_of_date = {
        'parts': ['year', 'month', 'day', 'hour', 'minute', 'second'],
        're': r'(\d+)\s*(?P<parts_of_date>\L<parts>)',
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

    _re_abbreviated_tz = {'re': r'\b(?P<tz>[A-Z]{3,4}|Z)\b'}

    date_parts = [
            r'{twelve_hour_time}',
            r'{twelve_hour}{minute}{second}',
            r'{time}',
            r'{utc_offset}',
            r'{abbreviated_tz}',
            r'{day_names}',
            # ABC - ACB - BCA - BAC - CAB - CBA  -- A day, B month, C year
            r'{day}{delimiter}(?:{month}|{month_names}){delimiter}{year}',  # ABC
            r'{day}{delimiter}{year}{delimiter}(?:{month}|{month_names})',  # ACB
            r'(?:{month}|{month_names}){delimiter}{year}{delimiter}{day}',  # BCA
            r'(?:{month}|{month_names}){delimiter}{day}{delimiter}{year}',  # BAC
            r'{year}{delimiter}{day}{delimiter}(?:{month}|{month_names})',  # CAB
            r'{year}{delimiter}(?:{month}|{month_names}){delimiter}{day}',  # CBA
    ]

    date_formats = [
        r'{year}{delimiter}(?:{month_names}|{month}){delimiter}{day}\s*{twelve_hour_time}\W*{abbreviated_tz}',
        r'{year}{delimiter}(?:{month_names}|{month}){delimiter}{day}\s*{twelve_hour_time}\W*{utc_offset}',
        r'{year}{delimiter}(?:{month_names}|{month}){delimiter}{day}\s*{time}\W*{abbreviated_tz}',
        r'{year}{delimiter}(?:{month_names}|{month}){delimiter}{day}\s*{time}\W*{utc_offset}',
        r'{year}{delimiter}(?:{month_names}|{month}){delimiter}{day}\s*{twelve_hour_time}',
        r'{year}{delimiter}(?:{month_names}|{month}){delimiter}{day}\s*{time}',
        r'{year}{delimiter}(?:{month_names}|{month}){delimiter}{day}',

        r'{year}{delimiter}{day}{delimiter}(?:{month_names}|{month})\s*{twelve_hour_time}\W*{abbreviated_tz}',
        r'{year}{delimiter}{day}{delimiter}(?:{month_names}|{month})\s*{twelve_hour_time}\W*{utc_offset}',
        r'{year}{delimiter}{day}{delimiter}(?:{month_names}|{month})\s*{time}\W*{abbreviated_tz}',
        r'{year}{delimiter}{day}{delimiter}(?:{month_names}|{month})\s*{time}\W*{utc_offset}',
        r'{year}{delimiter}{day}{delimiter}(?:{month_names}|{month})\s*{twelve_hour_time}',
        r'{year}{delimiter}{day}{delimiter}(?:{month_names}|{month})\s*{time}',
        r'{year}{delimiter}{day}{delimiter}(?:{month_names}|{month})',

        r'(?:{month_names}|{month}){delimiter}{day}{delimiter}{year}\s*{twelve_hour_time}\W*{abbreviated_tz}',
        r'(?:{month_names}|{month}){delimiter}{day}{delimiter}{year}\s*{twelve_hour_time}\W*{utc_offset}',
        r'(?:{month_names}|{month}){delimiter}{day}{delimiter}{year}\s*{time}\W*{abbreviated_tz}',
        r'(?:{month_names}|{month}){delimiter}{day}{delimiter}{year}\s*{time}\W*{utc_offset}',
        r'(?:{month_names}|{month}){delimiter}{day}{delimiter}{year}\s*{twelve_hour_time}',
        r'(?:{month_names}|{month}){delimiter}{day}{delimiter}{year}\s*{time}',
        r'(?:{month_names}|{month}){delimiter}{day}{delimiter}{year}',

        r'(?:{month_names}|{month}){delimiter}{year}{delimiter}{day}\s*{twelve_hour_time}\W*{abbreviated_tz}',
        r'(?:{month_names}|{month}){delimiter}{year}{delimiter}{day}\s*{twelve_hour_time}\W*{utc_offset}',
        r'(?:{month_names}|{month}){delimiter}{year}{delimiter}{day}\s*{time}\W*{abbreviated_tz}',
        r'(?:{month_names}|{month}){delimiter}{year}{delimiter}{day}\s*{time}\W*{utc_offset}',
        r'(?:{month_names}|{month}){delimiter}{year}{delimiter}{day}\s*{twelve_hour_time}',
        r'(?:{month_names}|{month}){delimiter}{year}{delimiter}{day}\s*{time}',
        r'(?:{month_names}|{month}){delimiter}{year}{delimiter}{day}',

        r'{day}{delimiter}{year}{delimiter}(?:{month_names}|{month})\s*{twelve_hour_time}\W*{abbreviated_tz}',
        r'{day}{delimiter}{year}{delimiter}(?:{month_names}|{month})\s*{twelve_hour_time}\W*{utc_offset}',
        r'{day}{delimiter}{year}{delimiter}(?:{month_names}|{month})\s*{time}\W*{abbreviated_tz}',
        r'{day}{delimiter}{year}{delimiter}(?:{month_names}|{month})\s*{time}\W*{utc_offset}',
        r'{day}{delimiter}{year}{delimiter}(?:{month_names}|{month})\s*{twelve_hour_time}',
        r'{day}{delimiter}{year}{delimiter}(?:{month_names}|{month})\s*{time}',
        r'{day}{delimiter}{year}{delimiter}(?:{month_names}|{month})',

        r'{day}{delimiter}(?:{month_names}|{month}){delimiter}{year}\s*{twelve_hour_time}\W*{abbreviated_tz}',
        r'{day}{delimiter}(?:{month_names}|{month}){delimiter}{year}\s*{twelve_hour_time}\W*{utc_offset}',
        r'{day}{delimiter}(?:{month_names}|{month}){delimiter}{year}\s*{time}\W*{abbreviated_tz}',
        r'{day}{delimiter}(?:{month_names}|{month}){delimiter}{year}\s*{time}\W*{utc_offset}',
        r'{day}{delimiter}(?:{month_names}|{month}){delimiter}{year}\s*{twelve_hour_time}',
        r'{day}{delimiter}(?:{month_names}|{month}){delimiter}{year}\s*{time}',
        r'{day}{delimiter}(?:{month_names}|{month}){delimiter}{year}',
    ]

    def __init__(self, date_string, enforce_format=True):
        self.date_string = date_string
        self._enforce_format = enforce_format

    def populate_regex_cache(self, patterns, cache_attr_name):
        cache_entry = []

        for pattern in patterns:
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

        setattr(self, cache_attr_name, cache_entry)

    def validate(self):
        if self._enforce_format:
            return self._validate(self.date_formats, '_formats_regex_cache')
        
    def _validate(self, patterns, cache_attr_name):
        results = []

        length_not_visited = len(self.date_string)
        start_index = 0

        if not getattr(self, cache_attr_name):
            self.populate_regex_cache(patterns, cache_attr_name)

        while length_not_visited > 0:
            for re_obj in getattr(self, cache_attr_name):
                match = re_obj.match(self.date_string[start_index:])
                if match:
                    length_not_visited -= match.span()[-1]
                    start_index += match.span()[-1]
                    results.append(match.capturesdict())
                    break
            else:
                length_not_visited = 0

        return results
