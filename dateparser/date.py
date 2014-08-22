#coding: utf-8
import re

from datetime import datetime
from dateutil.relativedelta import relativedelta

from .date_parser import DateParser
from .freshness_date_parser import freshness_date_parser


def sanitize_spaces(html_string):
    html_string = re.sub(u'\xa0', ' ', html_string)
    html_string = re.sub(r'\s+', ' ', html_string)
    html_string = re.sub(r'^\s+(\S.*?)\s+$', r'\1', html_string)
    return html_string


def date_range(begin, end, **kwargs):
    step = relativedelta(**kwargs) if kwargs else relativedelta(days=1)

    dateutil_error_prone_args = ['year', 'month', 'week', 'day', 'hour',
                                 'minute', 'second']
    for arg in dateutil_error_prone_args:
        if kwargs.has_key(arg):
            raise ValueError("Invalid argument: %s" % arg)

    date = begin
    while cmp(date, end) < 0:
        yield date
        date += step


def sanitize_date(date_string):
    date_string = re.sub(
        u'\t|\n|\r|\u00bb|\xe0|,\s\u0432|\u0433\.|\u200e|\xb7', ' ', date_string, flags=re.M
    )
    date_string = sanitize_spaces(date_string)
    date_string = re.sub('([AP]M).*', r'\1', date_string, flags=re.DOTALL)
    date_string = re.sub('^.*?on:\s+(.*)', r'\1', date_string)

    return date_string


def get_date_from_timestamp(date_string):
    if re.search('^\d{10}', date_string):
        return datetime.fromtimestamp(int(date_string[:10]))


def parse_with_formats(date_string, date_formats, final_call=False, alt_parser=None):
    """ Parse with formats and return depending on `final_call` arg.
    If final_call is True, return a dictionary with 'period' and 'obj_date'
    because these data won't be processed by any method outside.
    If final_call is False, return a 'obj_date' because it will be processed.

    :returns: :class:`datetime.datetime`, dict or None

    """
    #Encode to support locale setting in spiders
    data = {'period': 'day', 'date_obj': None}

    if isinstance(date_string, unicode):
        date_string = date_string.encode('utf-8')
    for date_format in date_formats:
        try:
            try:
                date_obj = datetime.strptime(date_string, date_format)
            except ValueError:
                alt_parser = alt_parser if alt_parser else DateParser()
                date_obj = alt_parser.parse(date_string, date_format=date_format)
            if final_call:
                data['date_obj'] = date_obj
                return data
            else:
                return date_obj
        except ValueError:
            continue
    else:
        if final_call:
            return data


class DateDataParser(object):

    def __init__(self, language=None):
        self.date_parser = DateParser(language)

    def get_date_data(self, date_string, date_formats=None):
        """ Return a dictionary with a date object and a period.
        Period values can be a 'day' (default), 'week', 'month', 'year'.
        It aims to solve the following issue:
        In example, a forum could displays "2 weeks ago" in the thread list
        (in the thread itself there's the right date) so the engine
        will translate "2 weeks ago" to a certain date.
        The next thread summary displays "3 weeks ago" which is translated
        to a other date seven days before first date.
        A valid date_string between both dates won't be scraped because
        it's not an exact date match. The period field helps to build
        better date range detection.

        TODO: Timezone issues

        """
        data = {'period': 'day', 'date_obj': None}
        #Detect timestamp date
        date_obj = get_date_from_timestamp(date_string)
        if date_obj:
            data['date_obj'] = date_obj
            return data

        date_string = date_string.strip()

        data_from_freshness = freshness_date_parser.get_date_data(date_string)
        if data_from_freshness['date_obj']:
            return data_from_freshness

        date_string = sanitize_date(date_string)

        #If known formats are provided, try them first
        if date_formats is not None:
            date_obj = parse_with_formats(date_string, date_formats,
                                          alt_parser=self.date_parser)
            if date_obj:
                data['date_obj'] = date_obj
                return data

        try:
            #Automatically detect date format
            date_obj = self.date_parser.parse(date_string)
            data['date_obj'] = date_obj.replace(tzinfo=None)
            return data
        except ValueError:
            #Try with hardcoded date formats
            additional_date_formats = [
                '%B %d, %Y, %I:%M:%S %p',
                '%b %d, %Y at %I:%M %p',
                '%d %B %Y %H:%M:%S',
                '%A, %B %d, %Y',
            ]
            return parse_with_formats(date_string, additional_date_formats, final_call=True)
        except TypeError:
            return data
