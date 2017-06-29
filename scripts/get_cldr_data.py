import requests
import re
import json
import os
import shutil
import time
from collections import OrderedDict

from utils import get_dict_difference
from order_languages import language_locale_dict

OAuth_Access_Token = 'OAuth_Access_Token'       # Add OAuth_Access_Token here
headers = {'Authorization': 'token %s' % OAuth_Access_Token}
cldr_dates_full_url = "https://api.github.com/repos/unicode-cldr/cldr-dates-full/contents/main/"

DATE_ORDER_PATTERN = re.compile(u'([DMY])+\u200f*[-/. \t]*([DMY])+\u200f*[-/. \t]*([DMY])+')
RELATIVE_PATTERN = re.compile(r'\{0\}')
AM_PATTERN = re.compile('\s*[aA]\.*\s*[mM]\.*\s*')
PM_PATTERN = re.compile('\s*[pP]\.*\s*[mM]\.*\s*')
DIGIT_PATTERN = re.compile(r'\d+$')


def retrieve_locale_data(locale):
    cldr_gregorian_url = cldr_dates_full_url + locale + "/ca-gregorian.json?ref=master"
    cldr_datefields_url = cldr_dates_full_url + locale + "/dateFields.json?ref=master"

    while(True):
        try:
            gregorian_response = requests.get(cldr_gregorian_url, headers=headers)
        except requests.exceptions.ConnectionError:
            print("Waiting...")
            time.sleep(5)
            continue
        break

    if gregorian_response.status_code != 200:
        raise RuntimeError("Bad Response " + str(gregorian_response.status_code))
    gregorian_content = gregorian_response.json()["content"].decode("base64")
    cldr_gregorian_data = json.loads(gregorian_content)
    json_dict = OrderedDict()
    gregorian_dict = cldr_gregorian_data["main"][locale]["dates"]["calendars"]["gregorian"]

    while(True):
        try:
            datefields_response = requests.get(cldr_datefields_url, headers=headers)
        except requests.exceptions.ConnectionError:
            print("Waiting...")
            time.sleep(5)
            continue
        break

    if datefields_response.status_code != 200:
        raise RuntimeError("Bad Response " + str(datefields_response.status_code))
    datefields_content = datefields_response.json()["content"].decode("base64")
    cldr_datefields_data = json.loads(datefields_content)

    date_fields_dict = cldr_datefields_data["main"][locale]["dates"]["fields"]

    json_dict["name"] = locale

    try:
        date_format_string = gregorian_dict.get("dateFormats").get("short").upper()
    except:
        date_format_string = gregorian_dict.get("dateFormats").get("short").get("_value").upper()

    json_dict["date_order"] = DATE_ORDER_PATTERN.sub(
            r'\1\2\3', DATE_ORDER_PATTERN.search(date_format_string).group())


    json_dict["january"] = [gregorian_dict.get("months").get("stand-alone").get("wide").get("1"),
                            gregorian_dict.get("months").get("stand-alone").get("abbreviated").get("1"),
                            gregorian_dict.get("months").get("stand-alone").get("narrow").get("1"),
                            gregorian_dict.get("months").get("format").get("wide").get("1"),
                            gregorian_dict.get("months").get("format").get("abbreviated").get("1"),
                            gregorian_dict.get("months").get("format").get("narrow").get("1")]

    json_dict["february"] = [gregorian_dict.get("months").get("stand-alone").get("wide").get("2"),
                             gregorian_dict.get("months").get("stand-alone").get("abbreviated").get("2"),
                             gregorian_dict.get("months").get("stand-alone").get("narrow").get("2"),
                             gregorian_dict.get("months").get("format").get("wide").get("2"),
                             gregorian_dict.get("months").get("format").get("abbreviated").get("2"),
                             gregorian_dict.get("months").get("format").get("narrow").get("2")]

    json_dict["march"] = [gregorian_dict.get("months").get("stand-alone").get("wide").get("3"),
                          gregorian_dict.get("months").get("stand-alone").get("abbreviated").get("3"),
                          gregorian_dict.get("months").get("stand-alone").get("narrow").get("3"),
                          gregorian_dict.get("months").get("format").get("wide").get("3"),
                          gregorian_dict.get("months").get("format").get("abbreviated").get("3"),
                          gregorian_dict.get("months").get("format").get("narrow").get("3")]

    json_dict["april"] = [gregorian_dict.get("months").get("stand-alone").get("wide").get("4"),
                          gregorian_dict.get("months").get("stand-alone").get("abbreviated").get("4"),
                          gregorian_dict.get("months").get("stand-alone").get("narrow").get("4"),
                          gregorian_dict.get("months").get("format").get("wide").get("4"),
                          gregorian_dict.get("months").get("format").get("abbreviated").get("4"),
                          gregorian_dict.get("months").get("format").get("narrow").get("4")]

    json_dict["may"] = [gregorian_dict.get("months").get("stand-alone").get("wide").get("5"),
                        gregorian_dict.get("months").get("stand-alone").get("abbreviated").get("5"),
                        gregorian_dict.get("months").get("stand-alone").get("narrow").get("5"),
                        gregorian_dict.get("months").get("format").get("wide").get("5"),
                        gregorian_dict.get("months").get("format").get("abbreviated").get("5"),
                        gregorian_dict.get("months").get("format").get("narrow").get("5")]

    json_dict["june"] = [gregorian_dict.get("months").get("stand-alone").get("wide").get("6"),
                         gregorian_dict.get("months").get("stand-alone").get("abbreviated").get("6"),
                         gregorian_dict.get("months").get("stand-alone").get("narrow").get("6"),
                         gregorian_dict.get("months").get("format").get("wide").get("6"),
                         gregorian_dict.get("months").get("format").get("abbreviated").get("6"),
                         gregorian_dict.get("months").get("format").get("narrow").get("6")]

    json_dict["july"] = [gregorian_dict.get("months").get("stand-alone").get("wide").get("7"),
                         gregorian_dict.get("months").get("stand-alone").get("abbreviated").get("7"),
                         gregorian_dict.get("months").get("stand-alone").get("narrow").get("7"),
                         gregorian_dict.get("months").get("format").get("wide").get("7"),
                         gregorian_dict.get("months").get("format").get("abbreviated").get("7"),
                         gregorian_dict.get("months").get("format").get("narrow").get("7")]

    json_dict["august"] = [gregorian_dict.get("months").get("stand-alone").get("wide").get("8"),
                           gregorian_dict.get("months").get("stand-alone").get("abbreviated").get("8"),
                           gregorian_dict.get("months").get("stand-alone").get("narrow").get("8"),
                           gregorian_dict.get("months").get("format").get("wide").get("8"),
                           gregorian_dict.get("months").get("format").get("abbreviated").get("8"),
                           gregorian_dict.get("months").get("format").get("narrow").get("8")]

    json_dict["september"] = [gregorian_dict.get("months").get("stand-alone").get("wide").get("9"),
                              gregorian_dict.get("months").get("stand-alone").get("abbreviated").get("9"),
                              gregorian_dict.get("months").get("stand-alone").get("narrow").get("9"),
                              gregorian_dict.get("months").get("format").get("wide").get("9"),
                              gregorian_dict.get("months").get("format").get("abbreviated").get("9"),
                              gregorian_dict.get("months").get("format").get("narrow").get("9")]

    json_dict["october"] = [gregorian_dict.get("months").get("stand-alone").get("wide").get("10"),
                            gregorian_dict.get("months").get("stand-alone").get("abbreviated").get("10"),
                            gregorian_dict.get("months").get("stand-alone").get("narrow").get("10"),
                            gregorian_dict.get("months").get("format").get("wide").get("10"),
                            gregorian_dict.get("months").get("format").get("abbreviated").get("10"),
                            gregorian_dict.get("months").get("format").get("narrow").get("10")]

    json_dict["november"] = [gregorian_dict.get("months").get("stand-alone").get("wide").get("11"),
                             gregorian_dict.get("months").get("stand-alone").get("abbreviated").get("11"),
                             gregorian_dict.get("months").get("stand-alone").get("narrow").get("11"),
                             gregorian_dict.get("months").get("format").get("wide").get("11"),
                             gregorian_dict.get("months").get("format").get("abbreviated").get("11"),
                             gregorian_dict.get("months").get("format").get("narrow").get("11")]

    json_dict["december"] = [gregorian_dict.get("months").get("stand-alone").get("wide").get("12"),
                             gregorian_dict.get("months").get("stand-alone").get("abbreviated").get("12"),
                             gregorian_dict.get("months").get("stand-alone").get("narrow").get("12"),
                             gregorian_dict.get("months").get("format").get("wide").get("12"),
                             gregorian_dict.get("months").get("format").get("abbreviated").get("12"),
                             gregorian_dict.get("months").get("format").get("narrow").get("12")]


    json_dict["monday"] = [gregorian_dict.get("days").get("stand-alone").get("wide").get("mon"),
                           gregorian_dict.get("days").get("stand-alone").get("abbreviated").get("mon"),
                           gregorian_dict.get("days").get("stand-alone").get("narrow").get("mon"),
                           gregorian_dict.get("days").get("format").get("wide").get("mon"),
                           gregorian_dict.get("days").get("format").get("abbreviated").get("mon"),
                           gregorian_dict.get("days").get("format").get("narrow").get("mon")]

    json_dict["tuesday"] = [gregorian_dict.get("days").get("stand-alone").get("wide").get("tue"),
                            gregorian_dict.get("days").get("stand-alone").get("abbreviated").get("tue"),
                            gregorian_dict.get("days").get("stand-alone").get("narrow").get("tue"),
                            gregorian_dict.get("days").get("format").get("wide").get("tue"),
                            gregorian_dict.get("days").get("format").get("abbreviated").get("tue"),
                            gregorian_dict.get("days").get("format").get("narrow").get("tue")]

    json_dict["wednesday"] = [gregorian_dict.get("days").get("stand-alone").get("wide").get("wed"),
                              gregorian_dict.get("days").get("stand-alone").get("abbreviated").get("wed"),
                              gregorian_dict.get("days").get("stand-alone").get("narrow").get("wed"),
                              gregorian_dict.get("days").get("format").get("wide").get("wed"),
                              gregorian_dict.get("days").get("format").get("abbreviated").get("wed"),
                              gregorian_dict.get("days").get("format").get("narrow").get("wed")]

    json_dict["thursday"] = [gregorian_dict.get("days").get("stand-alone").get("wide").get("thu"),
                             gregorian_dict.get("days").get("stand-alone").get("abbreviated").get("thu"),
                             gregorian_dict.get("days").get("stand-alone").get("narrow").get("thu"),
                             gregorian_dict.get("days").get("format").get("wide").get("thu"),
                             gregorian_dict.get("days").get("format").get("abbreviated").get("thu"),
                             gregorian_dict.get("days").get("format").get("narrow").get("thu")]

    json_dict["friday"] = [gregorian_dict.get("days").get("stand-alone").get("wide").get("fri"),
                           gregorian_dict.get("days").get("stand-alone").get("abbreviated").get("fri"),
                           gregorian_dict.get("days").get("stand-alone").get("narrow").get("fri"),
                           gregorian_dict.get("days").get("format").get("wide").get("fri"),
                           gregorian_dict.get("days").get("format").get("abbreviated").get("fri"),
                           gregorian_dict.get("days").get("format").get("narrow").get("fri")]

    json_dict["saturday"] = [gregorian_dict.get("days").get("stand-alone").get("wide").get("sat"),
                             gregorian_dict.get("days").get("stand-alone").get("abbreviated").get("sat"),
                             gregorian_dict.get("days").get("stand-alone").get("narrow").get("sat"),
                             gregorian_dict.get("days").get("format").get("wide").get("sat"),
                             gregorian_dict.get("days").get("format").get("abbreviated").get("sat"),
                             gregorian_dict.get("days").get("format").get("narrow").get("sat")]

    json_dict["sunday"] = [gregorian_dict.get("days").get("stand-alone").get("wide").get("sun"),
                           gregorian_dict.get("days").get("stand-alone").get("abbreviated").get("sun"),
                           gregorian_dict.get("days").get("stand-alone").get("narrow").get("sun"),
                           gregorian_dict.get("days").get("format").get("wide").get("sun"),
                           gregorian_dict.get("days").get("format").get("abbreviated").get("sun"),
                           gregorian_dict.get("days").get("format").get("narrow").get("sun")]

    json_dict["am"] = map(lambda x: AM_PATTERN.sub('am', x),
                          [gregorian_dict.get("dayPeriods").get("stand-alone").get("wide").get("am"),
                          gregorian_dict.get("dayPeriods").get("stand-alone").get("abbreviated").get("am"),
                          gregorian_dict.get("dayPeriods").get("stand-alone").get("narrow").get("am"),
                          gregorian_dict.get("dayPeriods").get("format").get("wide").get("am"),
                          gregorian_dict.get("dayPeriods").get("format").get("abbreviated").get("am"),
                          gregorian_dict.get("dayPeriods").get("format").get("narrow").get("am")])

    json_dict["pm"] = map(lambda x: PM_PATTERN.sub('pm', x),
                          [gregorian_dict.get("dayPeriods").get("stand-alone").get("wide").get("pm"),
                          gregorian_dict.get("dayPeriods").get("stand-alone").get("abbreviated").get("pm"),
                          gregorian_dict.get("dayPeriods").get("stand-alone").get("narrow").get("pm"),
                          gregorian_dict.get("dayPeriods").get("format").get("wide").get("pm"),
                          gregorian_dict.get("dayPeriods").get("format").get("abbreviated").get("pm"),
                          gregorian_dict.get("dayPeriods").get("format").get("narrow").get("pm")])

    json_dict["year"] = [date_fields_dict.get("year").get("displayName"),
                         date_fields_dict.get("year-short").get("displayName"),
                         date_fields_dict.get("year-narrow").get("displayName")]

    json_dict["month"] = [date_fields_dict.get("month").get("displayName"),
                          date_fields_dict.get("month-short").get("displayName"),
                          date_fields_dict.get("month-narrow").get("displayName")]

    json_dict["week"] = [date_fields_dict.get("week").get("displayName"),
                         date_fields_dict.get("week-short").get("displayName"),
                         date_fields_dict.get("week-narrow").get("displayName")]

    json_dict["day"] = [date_fields_dict.get("day").get("displayName"),
                        date_fields_dict.get("day-short").get("displayName"),
                        date_fields_dict.get("day-narrow").get("displayName")]

    json_dict["hour"] = [date_fields_dict.get("hour").get("displayName"),
                         date_fields_dict.get("hour-short").get("displayName"),
                         date_fields_dict.get("hour-narrow").get("displayName")]

    json_dict["minute"] = [date_fields_dict.get("minute").get("displayName"),
                           date_fields_dict.get("minute-short").get("displayName"),
                           date_fields_dict.get("minute-narrow").get("displayName")]

    json_dict["second"] = [date_fields_dict.get("second").get("displayName"),
                           date_fields_dict.get("second-short").get("displayName"),
                           date_fields_dict.get("second-narrow").get("displayName")]

    json_dict["relative-type"] = OrderedDict()

    json_dict["relative-type"]["1 year ago"] = [date_fields_dict.get("year").get("relative-type--1"),
                                                date_fields_dict.get("year-short").get("relative-type--1"),
                                                date_fields_dict.get("year-narrow").get("relative-type--1")]

    json_dict["relative-type"]["0 year ago"] = [date_fields_dict.get("year").get("relative-type-0"),
                                                date_fields_dict.get("year-short").get("relative-type-0"),
                                                date_fields_dict.get("year-narrow").get("relative-type-0")]

    json_dict["relative-type"]["in 1 year"] = [date_fields_dict.get("year").get("relative-type-1"),
                                               date_fields_dict.get("year-short").get("relative-type-1"),
                                               date_fields_dict.get("year-narrow").get("relative-type-1")]

    json_dict["relative-type"]["1 month ago"] = [date_fields_dict.get("month").get("relative-type--1"),
                                                 date_fields_dict.get("month-short").get("relative-type--1"),
                                                 date_fields_dict.get("month-narrow").get("relative-type--1")]

    json_dict["relative-type"]["0 month ago"] = [date_fields_dict.get("month").get("relative-type-0"),
                                                 date_fields_dict.get("month-short").get("relative-type-0"),
                                                 date_fields_dict.get("month-narrow").get("relative-type-0")]

    json_dict["relative-type"]["in 1 month"] = [date_fields_dict.get("month").get("relative-type-1"),
                                                date_fields_dict.get("month-short").get("relative-type-1"),
                                                date_fields_dict.get("month-narrow").get("relative-type-1")]

    json_dict["relative-type"]["1 week ago"] = [date_fields_dict.get("week").get("relative-type--1"),
                                                date_fields_dict.get("week-short").get("relative-type--1"),
                                                date_fields_dict.get("week-narrow").get("relative-type--1")]

    json_dict["relative-type"]["0 week ago"] = [date_fields_dict.get("week").get("relative-type-0"),
                                                date_fields_dict.get("week-short").get("relative-type-0"),
                                                date_fields_dict.get("week-narrow").get("relative-type-0")]

    json_dict["relative-type"]["in 1 week"] = [date_fields_dict.get("week").get("relative-type-1"),
                                               date_fields_dict.get("week-short").get("relative-type-1"),
                                               date_fields_dict.get("week-narrow").get("relative-type-1")]

    json_dict["relative-type"]["1 day ago"] = [date_fields_dict.get("day").get("relative-type--1"),
                                               date_fields_dict.get("day-short").get("relative-type--1"),
                                               date_fields_dict.get("day-narrow").get("relative-type--1")]

    json_dict["relative-type"]["0 day ago"] = [date_fields_dict.get("day").get("relative-type-0"),
                                               date_fields_dict.get("day-short").get("relative-type-0"),
                                               date_fields_dict.get("day-narrow").get("relative-type-0")]

    json_dict["relative-type"]["in 1 day"] = [date_fields_dict.get("day").get("relative-type-1"),
                                              date_fields_dict.get("day-short").get("relative-type-1"),
                                              date_fields_dict.get("day-narrow").get("relative-type-1")]

    json_dict["relative-type"]["0 hour ago"] = [date_fields_dict.get("hour").get("relative-type-0"),
                                                date_fields_dict.get("hour-short").get("relative-type-0"),
                                                date_fields_dict.get("hour-narrow").get("relative-type-0")]

    json_dict["relative-type"]["0 minute ago"] = [date_fields_dict.get("minute").get("relative-type-0"),
                                                  date_fields_dict.get("minute-short").get("relative-type-0"),
                                                  date_fields_dict.get("minute-narrow").get("relative-type-0")]

    json_dict["relative-type"]["0 second ago"] = [date_fields_dict.get("second").get("relative-type-0"),
                                                  date_fields_dict.get("second-short").get("relative-type-0"),
                                                  date_fields_dict.get("second-narrow").get("relative-type-0")]

    json_dict["relative-type"]["in \\1 year"] = (
        map(lambda x: RELATIVE_PATTERN.sub(r'(\d+)', x) if isinstance(x, basestring) else None,
            [date_fields_dict.get("year").get("relativeTime-type-future").get("relativeTimePattern-count-one"),
            date_fields_dict.get("year").get("relativeTime-type-future").get("relativeTimePattern-count-other"),
            date_fields_dict.get("year-short").get("relativeTime-type-future").get("relativeTimePattern-count-one"),
            date_fields_dict.get("year-short").get("relativeTime-type-future").get("relativeTimePattern-count-other"),
            date_fields_dict.get("year-narrow").get("relativeTime-type-future").get("relativeTimePattern-count-one"),
            date_fields_dict.get("year-narrow").get("relativeTime-type-future").get("relativeTimePattern-count-other")]))

    json_dict["relative-type"]["\\1 year ago"] = (
        map(lambda x: RELATIVE_PATTERN.sub(r'(\d+)', x) if isinstance(x, basestring) else None,
            [date_fields_dict.get("year").get("relativeTime-type-past").get("relativeTimePattern-count-one"),
            date_fields_dict.get("year").get("relativeTime-type-past").get("relativeTimePattern-count-other"),
            date_fields_dict.get("year-short").get("relativeTime-type-past").get("relativeTimePattern-count-one"),
            date_fields_dict.get("year-short").get("relativeTime-type-past").get("relativeTimePattern-count-other"),
            date_fields_dict.get("year-narrow").get("relativeTime-type-past").get("relativeTimePattern-count-one"),
            date_fields_dict.get("year-narrow").get("relativeTime-type-past").get("relativeTimePattern-count-other")]))

    json_dict["relative-type"]["in \\1 month"] = (
        map(lambda x: RELATIVE_PATTERN.sub(r'(\d+)', x) if isinstance(x, basestring) else None,
            [date_fields_dict.get("month").get("relativeTime-type-future").get("relativeTimePattern-count-one"),
            date_fields_dict.get("month").get("relativeTime-type-future").get("relativeTimePattern-count-other"),
            date_fields_dict.get("month-short").get("relativeTime-type-future").get("relativeTimePattern-count-one"),
            date_fields_dict.get("month-short").get("relativeTime-type-future").get("relativeTimePattern-count-other"),
            date_fields_dict.get("month-narrow").get("relativeTime-type-future").get("relativeTimePattern-count-one"),
            date_fields_dict.get("month-narrow").get("relativeTime-type-future").get("relativeTimePattern-count-other")]))

    json_dict["relative-type"]["\\1 month ago"] = (
        map(lambda x: RELATIVE_PATTERN.sub(r'(\d+)', x) if isinstance(x, basestring) else None,
            [date_fields_dict.get("month").get("relativeTime-type-past").get("relativeTimePattern-count-one"),
            date_fields_dict.get("month").get("relativeTime-type-past").get("relativeTimePattern-count-other"),
            date_fields_dict.get("month-short").get("relativeTime-type-past").get("relativeTimePattern-count-one"),
            date_fields_dict.get("month-short").get("relativeTime-type-past").get("relativeTimePattern-count-other"),
            date_fields_dict.get("month-narrow").get("relativeTime-type-past").get("relativeTimePattern-count-one"),
            date_fields_dict.get("month-narrow").get("relativeTime-type-past").get("relativeTimePattern-count-other")]))

    json_dict["relative-type"]["in \\1 week"] = (
        map(lambda x: RELATIVE_PATTERN.sub(r'(\d+)', x) if isinstance(x, basestring) else None,
            [date_fields_dict.get("week").get("relativeTime-type-future").get("relativeTimePattern-count-one"),
            date_fields_dict.get("week").get("relativeTime-type-future").get("relativeTimePattern-count-other"),
            date_fields_dict.get("week-short").get("relativeTime-type-future").get("relativeTimePattern-count-one"),
            date_fields_dict.get("week-short").get("relativeTime-type-future").get("relativeTimePattern-count-other"),
            date_fields_dict.get("week-narrow").get("relativeTime-type-future").get("relativeTimePattern-count-one"),
            date_fields_dict.get("week-narrow").get("relativeTime-type-future").get("relativeTimePattern-count-other")]))

    json_dict["relative-type"]["\\1 week ago"] = (
        map(lambda x: RELATIVE_PATTERN.sub(r'(\d+)', x) if isinstance(x, basestring) else None,
            [date_fields_dict.get("week").get("relativeTime-type-past").get("relativeTimePattern-count-one"),
            date_fields_dict.get("week").get("relativeTime-type-past").get("relativeTimePattern-count-other"),
            date_fields_dict.get("week-short").get("relativeTime-type-past").get("relativeTimePattern-count-one"),
            date_fields_dict.get("week-short").get("relativeTime-type-past").get("relativeTimePattern-count-other"),
            date_fields_dict.get("week-narrow").get("relativeTime-type-past").get("relativeTimePattern-count-one"),
            date_fields_dict.get("week-narrow").get("relativeTime-type-past").get("relativeTimePattern-count-other")]))

    json_dict["relative-type"]["in \\1 day"] = (
        map(lambda x: RELATIVE_PATTERN.sub(r'(\d+)', x) if isinstance(x, basestring) else None,
            [date_fields_dict.get("day").get("relativeTime-type-future").get("relativeTimePattern-count-one"),
            date_fields_dict.get("day").get("relativeTime-type-future").get("relativeTimePattern-count-other"),
            date_fields_dict.get("day-short").get("relativeTime-type-future").get("relativeTimePattern-count-one"),
            date_fields_dict.get("day-short").get("relativeTime-type-future").get("relativeTimePattern-count-other"),
            date_fields_dict.get("day-narrow").get("relativeTime-type-future").get("relativeTimePattern-count-one"),
            date_fields_dict.get("day-narrow").get("relativeTime-type-future").get("relativeTimePattern-count-other")]))

    json_dict["relative-type"]["\\1 day ago"] = (
        map(lambda x: RELATIVE_PATTERN.sub(r'(\d+)', x) if isinstance(x, basestring) else None,
            [date_fields_dict.get("day").get("relativeTime-type-past").get("relativeTimePattern-count-one"),
            date_fields_dict.get("day").get("relativeTime-type-past").get("relativeTimePattern-count-other"),
            date_fields_dict.get("day-short").get("relativeTime-type-past").get("relativeTimePattern-count-one"),
            date_fields_dict.get("day-short").get("relativeTime-type-past").get("relativeTimePattern-count-other"),
            date_fields_dict.get("day-narrow").get("relativeTime-type-past").get("relativeTimePattern-count-one"),
            date_fields_dict.get("day-narrow").get("relativeTime-type-past").get("relativeTimePattern-count-other")]))

    json_dict["relative-type"]["in \\1 hour"] = (
        map(lambda x: RELATIVE_PATTERN.sub(r'(\d+)', x) if isinstance(x, basestring) else None,
            [date_fields_dict.get("hour").get("relativeTime-type-future").get("relativeTimePattern-count-one"),
            date_fields_dict.get("hour").get("relativeTime-type-future").get("relativeTimePattern-count-other"),
            date_fields_dict.get("hour-short").get("relativeTime-type-future").get("relativeTimePattern-count-one"),
            date_fields_dict.get("hour-short").get("relativeTime-type-future").get("relativeTimePattern-count-other"),
            date_fields_dict.get("hour-narrow").get("relativeTime-type-future").get("relativeTimePattern-count-one"),
            date_fields_dict.get("hour-narrow").get("relativeTime-type-future").get("relativeTimePattern-count-other")]))

    json_dict["relative-type"]["\\1 hour ago"] = (
        map(lambda x: RELATIVE_PATTERN.sub(r'(\d+)', x) if isinstance(x, basestring) else None,
            [date_fields_dict.get("hour").get("relativeTime-type-past").get("relativeTimePattern-count-one"),
            date_fields_dict.get("hour").get("relativeTime-type-past").get("relativeTimePattern-count-other"),
            date_fields_dict.get("hour-short").get("relativeTime-type-past").get("relativeTimePattern-count-one"),
            date_fields_dict.get("hour-short").get("relativeTime-type-past").get("relativeTimePattern-count-other"),
            date_fields_dict.get("hour-narrow").get("relativeTime-type-past").get("relativeTimePattern-count-one"),
            date_fields_dict.get("hour-narrow").get("relativeTime-type-past").get("relativeTimePattern-count-other")]))

    json_dict["relative-type"]["in \\1 minute"] = (
        map(lambda x: RELATIVE_PATTERN.sub(r'(\d+)', x) if isinstance(x, basestring) else None,
            [date_fields_dict.get("minute").get("relativeTime-type-future").get("relativeTimePattern-count-one"),
            date_fields_dict.get("minute").get("relativeTime-type-future").get("relativeTimePattern-count-other"),
            date_fields_dict.get("minute-short").get("relativeTime-type-future").get("relativeTimePattern-count-one"),
            date_fields_dict.get("minute-short").get("relativeTime-type-future").get("relativeTimePattern-count-other"),
            date_fields_dict.get("minute-narrow").get("relativeTime-type-future").get("relativeTimePattern-count-one"),
            date_fields_dict.get("minute-narrow").get("relativeTime-type-future").get("relativeTimePattern-count-other")]))

    json_dict["relative-type"]["\\1 minute ago"] = (
        map(lambda x: RELATIVE_PATTERN.sub(r'(\d+)', x) if isinstance(x, basestring) else None,
            [date_fields_dict.get("minute").get("relativeTime-type-past").get("relativeTimePattern-count-one"),
            date_fields_dict.get("minute").get("relativeTime-type-past").get("relativeTimePattern-count-other"),
            date_fields_dict.get("minute-short").get("relativeTime-type-past").get("relativeTimePattern-count-one"),
            date_fields_dict.get("minute-short").get("relativeTime-type-past").get("relativeTimePattern-count-other"),
            date_fields_dict.get("minute-narrow").get("relativeTime-type-past").get("relativeTimePattern-count-one"),
            date_fields_dict.get("minute-narrow").get("relativeTime-type-past").get("relativeTimePattern-count-other")]))

    json_dict["relative-type"]["in \\1 second"] = (
        map(lambda x: RELATIVE_PATTERN.sub(r'(\d+)', x) if isinstance(x, basestring) else None,
            [date_fields_dict.get("second").get("relativeTime-type-future").get("relativeTimePattern-count-one"),
            date_fields_dict.get("second").get("relativeTime-type-future").get("relativeTimePattern-count-other"),
            date_fields_dict.get("second-short").get("relativeTime-type-future").get("relativeTimePattern-count-one"),
            date_fields_dict.get("second-short").get("relativeTime-type-future").get("relativeTimePattern-count-other"),
            date_fields_dict.get("second-narrow").get("relativeTime-type-future").get("relativeTimePattern-count-one"),
            date_fields_dict.get("second-narrow").get("relativeTime-type-future").get("relativeTimePattern-count-other")]))

    json_dict["relative-type"]["\\1 second ago"] = (
        map(lambda x: RELATIVE_PATTERN.sub(r'(\d+)', x) if isinstance(x, basestring) else None,
            [date_fields_dict.get("second").get("relativeTime-type-past").get("relativeTimePattern-count-one"),
            date_fields_dict.get("second").get("relativeTime-type-past").get("relativeTimePattern-count-other"),
            date_fields_dict.get("second-short").get("relativeTime-type-past").get("relativeTimePattern-count-one"),
            date_fields_dict.get("second-short").get("relativeTime-type-past").get("relativeTimePattern-count-other"),
            date_fields_dict.get("second-narrow").get("relativeTime-type-past").get("relativeTimePattern-count-one"),
            date_fields_dict.get("second-narrow").get("relativeTime-type-past").get("relativeTimePattern-count-other")]))

    return json_dict


def clean_dict(json_dict):
    for key, value in json_dict.items():
        if isinstance(value, list):
            value = [i for i in value if isinstance(i, basestring) and not DIGIT_PATTERN.match(i)]
            json_dict[key] = list(set(map(
                lambda y: ' '.join(map(lambda x: x.rstrip('.'), y.lower().split())), value)))
        elif isinstance(value, dict):
            json_dict[key] = clean_dict(value)
    return json_dict


def main():
    os.chdir(os.path.dirname(__file__))
    parent_directory = "../data/cldr_language_data"
    directory = "../data/cldr_language_data/date_translation_data/"
    if not os.path.isdir(parent_directory):
        os.mkdir(parent_directory)
    if os.path.isdir(directory):
        shutil.rmtree(directory)
    os.mkdir(directory)

    for language in language_locale_dict:
        json_language_dict = clean_dict(retrieve_locale_data(language))
        locale_specific_dict = OrderedDict()
        locales_list = language_locale_dict[language]
        for locale in locales_list:
            json_locale_dict = clean_dict(retrieve_locale_data(locale))
            locale_specific_dict[locale] = get_dict_difference(json_language_dict, json_locale_dict)
        json_language_dict["locale_specific"] = locale_specific_dict
        filename = directory + language + ".json"
        print("writing " + filename)
        json_string = json.dumps(json_language_dict, indent=4, ensure_ascii=False).encode('utf-8')
        with open(filename, 'w') as f:
            f.write(json_string)


if __name__ == '__main__':
    main()
