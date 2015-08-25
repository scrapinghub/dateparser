import regex

class DateValidator(object):

    _regex_cache = []

    _delimiters = [',', '-', '/', '\\', '.']
    _re_delimiters = r'(?P<delimiter>\L<delimiters>)'

    _re_year = r'(?P<year>\b(?:\d{2}|\d{4})\b)'
    _re_month = r'(?P<month>\b(?:0?[1-9]|1[0-2])\b)'
    _re_day = r'(?P<day>\b(?:[1-9]|[0-2][0-9]|3[0-1])\b)'

    _re_hour = r'(?P<hour>\b(?:2[0-3]|[0-1]?[0-9])\b)'
    _re_minute = r'(?P<minute>\b(?:[0-5]?[0-9])\b)'
    _re_second = r'(?P<second>\b(?:[0-5]?[0-9]|60)\b)'

    def __init__(self, date_string):
        self.date_string = date_string

    def validate(self):
        results = {}

        if not self._regex_cache:
            self.populate_regex_cache()

        while self.date_string:
            for re_obj in self._regex_cache:
                match = re_obj.match(self.date_string)
                if not match:
                    continue

                self.date_string = self.date_string[match.spans()[0][-1]:]
                results.update(match.capturesdict())

        return results

    def populate_regex_cache(self):
        cache_entry = []

        # year - month - day
        cache_entry.append(
            regex.compile(r'{year}{delimiter}{month}\g<delimiter>{day}'
                        .format(
                            year=self._re_year,
                            month=self._re_month,
                            day=self._re_day,
                            delimiter=self._re_delimiters),
                        delimiters=self._delimiters,
                        flags=regex.V1 | regex.DOTALL)
        )

        # year - day - month
        cache_entry.append(
            regex.compile(r'{year}{delimiter}{day}\g<delimiter>{month}'
                        .format(
                            year=self._re_year,
                            month=self._re_month,
                            day=self._re_day,
                            delimiter=self._re_delimiters),
                        delimiters=self._delimiters,
                        flags=regex.V1 | regex.DOTALL)
        )

        # day - month - year
        cache_entry.append(
        regex.compile(r'{day}{delimiter}{month}\g<delimiter>{year}'
                      .format(
                            year=self._re_year,
                            month=self._re_month,
                            day=self._re_day,
                            delimiter=self._re_delimiters),
                        delimiters=self._delimiters,
                        flags=regex.V1 | regex.DOTALL)
        )

        # month - day - year
        cache_entry.append(
        regex.compile(r'{month}{delimiter}{day}\g<delimiter>{year}'
                      .format(
                            year=self._re_year,
                            month=self._re_month,
                            day=self._re_day,
                            delimiter=self._re_delimiters),
                        delimiters=self._delimiters,
                        flags=regex.V1 | regex.DOTALL)
        )

        self._regex_cache.extend(cache_entry)
