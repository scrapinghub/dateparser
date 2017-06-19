import requests
import re
import json
import os
import shutil
import time
from collections import OrderedDict

OAuth_Access_Token = 'OAuth_Access_Token'       #Add OAuth_Access_Token here
headers = {'Authorization':'token %s' % OAuth_Access_Token}
cldr_dates_full_url = "https://api.github.com/repos/unicode-cldr/cldr-dates-full/contents/main/"

DATE_ORDER_PATTERN = re.compile(u'([DMY])+\u200f*[-/. \t]*([DMY])+\u200f*[-/. \t]*([DMY])+')


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
        raise RuntimeError("Bad Response " + str(response.status_code))
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

    if datefields_response.status_code !=200:
        raise RuntimeError("Bad Response " + str(response.status_code))
    datefields_content = datefields_response.json()["content"].decode("base64")
    cldr_datefields_data = json.loads(datefields_content)

    date_fields_dict = cldr_datefields_data["main"][locale]["dates"]["fields"]

    json_dict["name"] = locale

    try:
        date_format_string = gregorian_dict.get("dateFormats").get("short").upper()
    except:
        date_format_string = gregorian_dict.get("dateFormats").get("short").get("_value").upper()

    json_dict["date_order"] = DATE_ORDER_PATTERN.sub(r'\1\2\3', DATE_ORDER_PATTERN.search(date_format_string).group())


    json_dict["january"] = list(set([gregorian_dict.get("months").get("stand-alone").get("wide").get("1"),
                                     gregorian_dict.get("months").get("stand-alone").get("abbreviated").get("1"),
                                     gregorian_dict.get("months").get("stand-alone").get("narrow").get("1"),
                                     gregorian_dict.get("months").get("format").get("wide").get("1"),
                                     gregorian_dict.get("months").get("format").get("abbreviated").get("1"),
                                     gregorian_dict.get("months").get("format").get("narrow").get("1")]))

    json_dict["february"] = list(set([gregorian_dict.get("months").get("stand-alone").get("wide").get("2"),
                                      gregorian_dict.get("months").get("stand-alone").get("abbreviated").get("2"),
                                      gregorian_dict.get("months").get("stand-alone").get("narrow").get("2"),
                                      gregorian_dict.get("months").get("format").get("wide").get("2"),
                                      gregorian_dict.get("months").get("format").get("abbreviated").get("2"),
                                      gregorian_dict.get("months").get("format").get("narrow").get("2")]))

    json_dict["march"] = list(set([gregorian_dict.get("months").get("stand-alone").get("wide").get("3"),
                                   gregorian_dict.get("months").get("stand-alone").get("abbreviated").get("3"),
                                   gregorian_dict.get("months").get("stand-alone").get("narrow").get("3"),
                                   gregorian_dict.get("months").get("format").get("wide").get("3"),
                                   gregorian_dict.get("months").get("format").get("abbreviated").get("3"),
                                   gregorian_dict.get("months").get("format").get("narrow").get("3")]))

    json_dict["april"] = list(set([gregorian_dict.get("months").get("stand-alone").get("wide").get("4"),
                                   gregorian_dict.get("months").get("stand-alone").get("abbreviated").get("4"),
                                   gregorian_dict.get("months").get("stand-alone").get("narrow").get("4"),
                                   gregorian_dict.get("months").get("format").get("wide").get("4"),
                                   gregorian_dict.get("months").get("format").get("abbreviated").get("4"),
                                   gregorian_dict.get("months").get("format").get("narrow").get("4")]))

    json_dict["may"] = list(set([gregorian_dict.get("months").get("stand-alone").get("wide").get("5"),
                                 gregorian_dict.get("months").get("stand-alone").get("abbreviated").get("5"),
                                 gregorian_dict.get("months").get("stand-alone").get("narrow").get("5"),
                                 gregorian_dict.get("months").get("format").get("wide").get("5"),
                                 gregorian_dict.get("months").get("format").get("abbreviated").get("5"),
                                 gregorian_dict.get("months").get("format").get("narrow").get("5")]))

    json_dict["june"] = list(set([gregorian_dict.get("months").get("stand-alone").get("wide").get("6"),
                                  gregorian_dict.get("months").get("stand-alone").get("abbreviated").get("6"),
                                  gregorian_dict.get("months").get("stand-alone").get("narrow").get("6"),
                                  gregorian_dict.get("months").get("format").get("wide").get("6"),
                                  gregorian_dict.get("months").get("format").get("abbreviated").get("6"),
                                  gregorian_dict.get("months").get("format").get("narrow").get("6")]))

    json_dict["july"] = list(set([gregorian_dict.get("months").get("stand-alone").get("wide").get("7"),
                                  gregorian_dict.get("months").get("stand-alone").get("abbreviated").get("7"),
                                  gregorian_dict.get("months").get("stand-alone").get("narrow").get("7"),
                                  gregorian_dict.get("months").get("format").get("wide").get("7"),
                                  gregorian_dict.get("months").get("format").get("abbreviated").get("7"),
                                  gregorian_dict.get("months").get("format").get("narrow").get("7")]))

    json_dict["august"] = list(set([gregorian_dict.get("months").get("stand-alone").get("wide").get("8"),
                                    gregorian_dict.get("months").get("stand-alone").get("abbreviated").get("8"),
                                    gregorian_dict.get("months").get("stand-alone").get("narrow").get("8"),
                                    gregorian_dict.get("months").get("format").get("wide").get("8"),
                                    gregorian_dict.get("months").get("format").get("abbreviated").get("8"),
                                    gregorian_dict.get("months").get("format").get("narrow").get("8")]))

    json_dict["september"] = list(set([gregorian_dict.get("months").get("stand-alone").get("wide").get("9"),
                                       gregorian_dict.get("months").get("stand-alone").get("abbreviated").get("9"),
                                       gregorian_dict.get("months").get("stand-alone").get("narrow").get("9"),
                                       gregorian_dict.get("months").get("format").get("wide").get("9"),
                                       gregorian_dict.get("months").get("format").get("abbreviated").get("9"),
                                       gregorian_dict.get("months").get("format").get("narrow").get("9")]))

    json_dict["october"] = list(set([gregorian_dict.get("months").get("stand-alone").get("wide").get("10"),
                                     gregorian_dict.get("months").get("stand-alone").get("abbreviated").get("10"),
                                     gregorian_dict.get("months").get("stand-alone").get("narrow").get("10"),
                                     gregorian_dict.get("months").get("format").get("wide").get("10"),
                                     gregorian_dict.get("months").get("format").get("abbreviated").get("10"),
                                     gregorian_dict.get("months").get("format").get("narrow").get("10")]))

    json_dict["november"] = list(set([gregorian_dict.get("months").get("stand-alone").get("wide").get("11"),
                                      gregorian_dict.get("months").get("stand-alone").get("abbreviated").get("11"),
                                      gregorian_dict.get("months").get("stand-alone").get("narrow").get("11"),
                                      gregorian_dict.get("months").get("format").get("wide").get("11"),
                                      gregorian_dict.get("months").get("format").get("abbreviated").get("11"),
                                      gregorian_dict.get("months").get("format").get("narrow").get("11")]))

    json_dict["december"] = list(set([gregorian_dict.get("months").get("stand-alone").get("wide").get("12"),
                                      gregorian_dict.get("months").get("stand-alone").get("abbreviated").get("12"),
                                      gregorian_dict.get("months").get("stand-alone").get("narrow").get("12"),
                                      gregorian_dict.get("months").get("format").get("wide").get("12"),
                                      gregorian_dict.get("months").get("format").get("abbreviated").get("12"),
                                      gregorian_dict.get("months").get("format").get("narrow").get("12")]))


    json_dict["monday"] = list(set([gregorian_dict.get("days").get("stand-alone").get("wide").get("mon"),
                                    gregorian_dict.get("days").get("stand-alone").get("abbreviated").get("mon"),
                                    gregorian_dict.get("days").get("stand-alone").get("narrow").get("mon"),
                                    gregorian_dict.get("days").get("format").get("wide").get("mon"),
                                    gregorian_dict.get("days").get("format").get("abbreviated").get("mon"),
                                    gregorian_dict.get("days").get("format").get("narrow").get("mon")]))

    json_dict["tuesday"] = list(set([gregorian_dict.get("days").get("stand-alone").get("wide").get("tue"),
                                     gregorian_dict.get("days").get("stand-alone").get("abbreviated").get("tue"),
                                     gregorian_dict.get("days").get("stand-alone").get("narrow").get("tue"),
                                     gregorian_dict.get("days").get("format").get("wide").get("tue"),
                                     gregorian_dict.get("days").get("format").get("abbreviated").get("tue"),
                                     gregorian_dict.get("days").get("format").get("narrow").get("tue")]))

    json_dict["wednesday"] = list(set([gregorian_dict.get("days").get("stand-alone").get("wide").get("wed"),
                                       gregorian_dict.get("days").get("stand-alone").get("abbreviated").get("wed"),
                                       gregorian_dict.get("days").get("stand-alone").get("narrow").get("wed"),
                                       gregorian_dict.get("days").get("format").get("wide").get("wed"),
                                       gregorian_dict.get("days").get("format").get("abbreviated").get("wed"),
                                       gregorian_dict.get("days").get("format").get("narrow").get("wed")]))

    json_dict["thursday"] = list(set([gregorian_dict.get("days").get("stand-alone").get("wide").get("thu"),
                                      gregorian_dict.get("days").get("stand-alone").get("abbreviated").get("thu"),
                                      gregorian_dict.get("days").get("stand-alone").get("narrow").get("thu"),
                                      gregorian_dict.get("days").get("format").get("wide").get("thu"),
                                      gregorian_dict.get("days").get("format").get("abbreviated").get("thu"),
                                      gregorian_dict.get("days").get("format").get("narrow").get("thu")]))

    json_dict["friday"] = list(set([gregorian_dict.get("days").get("stand-alone").get("wide").get("fri"),
                                    gregorian_dict.get("days").get("stand-alone").get("abbreviated").get("fri"),
                                    gregorian_dict.get("days").get("stand-alone").get("narrow").get("fri"),
                                    gregorian_dict.get("days").get("format").get("wide").get("fri"),
                                    gregorian_dict.get("days").get("format").get("abbreviated").get("fri"),
                                    gregorian_dict.get("days").get("format").get("narrow").get("fri")]))

    json_dict["saturday"] = list(set([gregorian_dict.get("days").get("stand-alone").get("wide").get("sat"),
                                      gregorian_dict.get("days").get("stand-alone").get("abbreviated").get("sat"),
                                      gregorian_dict.get("days").get("stand-alone").get("narrow").get("sat"),
                                      gregorian_dict.get("days").get("format").get("wide").get("sat"),
                                      gregorian_dict.get("days").get("format").get("abbreviated").get("sat"),
                                      gregorian_dict.get("days").get("format").get("narrow").get("sat")]))

    json_dict["sunday"] = list(set([gregorian_dict.get("days").get("stand-alone").get("wide").get("sun"),
                                    gregorian_dict.get("days").get("stand-alone").get("abbreviated").get("sun"),
                                    gregorian_dict.get("days").get("stand-alone").get("narrow").get("sun"),
                                    gregorian_dict.get("days").get("format").get("wide").get("sun"),
                                    gregorian_dict.get("days").get("format").get("abbreviated").get("sun"),
                                    gregorian_dict.get("days").get("format").get("narrow").get("sun")]))

    json_dict["am"] = list(set([gregorian_dict.get("dayPeriods").get("stand-alone").get("wide").get("am"),
                                    gregorian_dict.get("dayPeriods").get("stand-alone").get("abbreviated").get("am"),
                                    gregorian_dict.get("dayPeriods").get("stand-alone").get("narrow").get("am"),
                                    gregorian_dict.get("dayPeriods").get("format").get("wide").get("am"),
                                    gregorian_dict.get("dayPeriods").get("format").get("abbreviated").get("am"),
                                    gregorian_dict.get("dayPeriods").get("format").get("narrow").get("am")]))

    json_dict["pm"] = list(set([gregorian_dict.get("dayPeriods").get("stand-alone").get("wide").get("pm"),
                                    gregorian_dict.get("dayPeriods").get("stand-alone").get("abbreviated").get("pm"),
                                    gregorian_dict.get("dayPeriods").get("stand-alone").get("narrow").get("pm"),
                                    gregorian_dict.get("dayPeriods").get("format").get("wide").get("pm"),
                                    gregorian_dict.get("dayPeriods").get("format").get("abbreviated").get("pm"),
                                    gregorian_dict.get("dayPeriods").get("format").get("narrow").get("pm")]))

    json_dict["year"] = list(set([date_fields_dict.get("year").get("displayName"),
                                  date_fields_dict.get("year-short").get("displayName"),
                                  date_fields_dict.get("year-narrow").get("displayName")]))

    json_dict["month"] = list(set([date_fields_dict.get("month").get("displayName"),
                                   date_fields_dict.get("month-short").get("displayName"),
                                   date_fields_dict.get("month-narrow").get("displayName")]))

    json_dict["week"] = list(set([date_fields_dict.get("week").get("displayName"),
                                  date_fields_dict.get("week-short").get("displayName"),
                                  date_fields_dict.get("week-narrow").get("displayName")]))

    json_dict["day"] = list(set([date_fields_dict.get("day").get("displayName"),
                                 date_fields_dict.get("day-short").get("displayName"),
                                 date_fields_dict.get("day-narrow").get("displayName")]))

    json_dict["hour"] = list(set([date_fields_dict.get("hour").get("displayName"),
                                 date_fields_dict.get("hour-short").get("displayName"),
                                 date_fields_dict.get("hour-narrow").get("displayName")]))

    json_dict["minute"] = list(set([date_fields_dict.get("minute").get("displayName"),
                                 date_fields_dict.get("minute-short").get("displayName"),
                                 date_fields_dict.get("minute-narrow").get("displayName")]))

    json_dict["second"] = list(set([date_fields_dict.get("second").get("displayName"),
                                 date_fields_dict.get("second-short").get("displayName"),
                                 date_fields_dict.get("second-narrow").get("displayName")]))

    json_dict["relative-type"] = OrderedDict()

    json_dict["relative-type"]["1 year ago"] = list(set([date_fields_dict.get("year").get("relative-type--1"),
                                                         date_fields_dict.get("year-short").get("relative-type--1"),
                                                         date_fields_dict.get("year-narrow").get("relative-type--1")]))

    json_dict["relative-type"]["0 year ago"] = list(set([date_fields_dict.get("year").get("relative-type-0"),
                                                         date_fields_dict.get("year-short").get("relative-type-0"),
                                                         date_fields_dict.get("year-narrow").get("relative-type-0")]))

    json_dict["relative-type"]["in 1 year"] = list(set([date_fields_dict.get("year").get("relative-type-1"),
                                                         date_fields_dict.get("year-short").get("relative-type-1"),
                                                         date_fields_dict.get("year-narrow").get("relative-type-1")]))

    json_dict["relative-type"]["1 month ago"] = list(set([date_fields_dict.get("month").get("relative-type--1"),
                                                         date_fields_dict.get("month-short").get("relative-type--1"),
                                                         date_fields_dict.get("month-narrow").get("relative-type--1")]))

    json_dict["relative-type"]["0 month ago"] = list(set([date_fields_dict.get("month").get("relative-type-0"),
                                                         date_fields_dict.get("month-short").get("relative-type-0"),
                                                         date_fields_dict.get("month-narrow").get("relative-type-0")]))

    json_dict["relative-type"]["in 1 month"] = list(set([date_fields_dict.get("month").get("relative-type-1"),
                                                         date_fields_dict.get("month-short").get("relative-type-1"),
                                                         date_fields_dict.get("month-narrow").get("relative-type-1")]))

    json_dict["relative-type"]["1 week ago"] = list(set([date_fields_dict.get("week").get("relative-type--1"),
                                                         date_fields_dict.get("week-short").get("relative-type--1"),
                                                         date_fields_dict.get("week-narrow").get("relative-type--1")]))

    json_dict["relative-type"]["0 week ago"] = list(set([date_fields_dict.get("week").get("relative-type-0"),
                                                         date_fields_dict.get("week-short").get("relative-type-0"),
                                                         date_fields_dict.get("week-narrow").get("relative-type-0")]))

    json_dict["relative-type"]["in 1 week"] = list(set([date_fields_dict.get("week").get("relative-type-1"),
                                                         date_fields_dict.get("week-short").get("relative-type-1"),
                                                         date_fields_dict.get("week-narrow").get("relative-type-1")]))

    json_dict["relative-type"]["1 day ago"] = list(set([date_fields_dict.get("day").get("relative-type--1"),
                                                         date_fields_dict.get("day-short").get("relative-type--1"),
                                                         date_fields_dict.get("day-narrow").get("relative-type--1")]))

    json_dict["relative-type"]["0 day ago"] = list(set([date_fields_dict.get("day").get("relative-type-0"),
                                                         date_fields_dict.get("day-short").get("relative-type-0"),
                                                         date_fields_dict.get("day-narrow").get("relative-type-0")]))

    json_dict["relative-type"]["in 1 day"] = list(set([date_fields_dict.get("day").get("relative-type-1"),
                                                         date_fields_dict.get("day-short").get("relative-type-1"),
                                                         date_fields_dict.get("day-narrow").get("relative-type-1")]))

    json_dict["relative-type"]["0 hour ago"] = list(set([date_fields_dict.get("hour").get("relative-type-0"),
                                                         date_fields_dict.get("hour-short").get("relative-type-0"),
                                                         date_fields_dict.get("hour-narrow").get("relative-type-0")]))

    json_dict["relative-type"]["0 minute ago"] = list(set([date_fields_dict.get("minute").get("relative-type-0"),
                                                         date_fields_dict.get("minute-short").get("relative-type-0"),
                                                         date_fields_dict.get("minute-narrow").get("relative-type-0")]))

    json_dict["relative-type"]["0 second ago"] = list(set([date_fields_dict.get("second").get("relative-type-0"),
                                                         date_fields_dict.get("second-short").get("relative-type-0"),
                                                         date_fields_dict.get("second-narrow").get("relative-type-0")]))


    json_dict["relative-type"]["in \\1 year"] = list(set(map(lambda x:re.sub(r'\{0\}', r'(\d+)',x) if (isinstance(x,str) or isinstance(x,unicode)) else None,
                                                [date_fields_dict.get("year").get("relativeTime-type-future").get("relativeTimePattern-count-one"),
                                                 date_fields_dict.get("year").get("relativeTime-type-future").get("relativeTimePattern-count-other"),
                                                 date_fields_dict.get("year-short").get("relativeTime-type-future").get("relativeTimePattern-count-one"),
                                                 date_fields_dict.get("year-short").get("relativeTime-type-future").get("relativeTimePattern-count-other"),
                                                 date_fields_dict.get("year-narrow").get("relativeTime-type-future").get("relativeTimePattern-count-one"),
                                                 date_fields_dict.get("year-narrow").get("relativeTime-type-future").get("relativeTimePattern-count-other")])))

    json_dict["relative-type"]["\\1 year ago"] = list(set(map(lambda x:re.sub(r'\{0\}', r'(\d+)',x) if (isinstance(x,str) or isinstance(x,unicode)) else None,
                                                [date_fields_dict.get("year").get("relativeTime-type-past").get("relativeTimePattern-count-one"),
                                                 date_fields_dict.get("year").get("relativeTime-type-past").get("relativeTimePattern-count-other"),
                                                 date_fields_dict.get("year-short").get("relativeTime-type-past").get("relativeTimePattern-count-one"),
                                                 date_fields_dict.get("year-short").get("relativeTime-type-past").get("relativeTimePattern-count-other"),
                                                 date_fields_dict.get("year-narrow").get("relativeTime-type-past").get("relativeTimePattern-count-one"),
                                                 date_fields_dict.get("year-narrow").get("relativeTime-type-past").get("relativeTimePattern-count-other")])))


    json_dict["relative-type"]["in \\1 month"] = list(set(map(lambda x:re.sub(r'\{0\}', r'(\d+)',x) if (isinstance(x,str) or isinstance(x,unicode)) else None,
                                                [date_fields_dict.get("month").get("relativeTime-type-future").get("relativeTimePattern-count-one"),
                                                 date_fields_dict.get("month").get("relativeTime-type-future").get("relativeTimePattern-count-other"),
                                                 date_fields_dict.get("month-short").get("relativeTime-type-future").get("relativeTimePattern-count-one"),
                                                 date_fields_dict.get("month-short").get("relativeTime-type-future").get("relativeTimePattern-count-other"),
                                                 date_fields_dict.get("month-narrow").get("relativeTime-type-future").get("relativeTimePattern-count-one"),
                                                 date_fields_dict.get("month-narrow").get("relativeTime-type-future").get("relativeTimePattern-count-other")])))

    json_dict["relative-type"]["\\1 month ago"] = list(set(map(lambda x:re.sub(r'\{0\}', r'(\d+)',x) if (isinstance(x,str) or isinstance(x,unicode)) else None,
                                                [date_fields_dict.get("month").get("relativeTime-type-past").get("relativeTimePattern-count-one"),
                                                 date_fields_dict.get("month").get("relativeTime-type-past").get("relativeTimePattern-count-other"),
                                                 date_fields_dict.get("month-short").get("relativeTime-type-past").get("relativeTimePattern-count-one"),
                                                 date_fields_dict.get("month-short").get("relativeTime-type-past").get("relativeTimePattern-count-other"),
                                                 date_fields_dict.get("month-narrow").get("relativeTime-type-past").get("relativeTimePattern-count-one"),
                                                 date_fields_dict.get("month-narrow").get("relativeTime-type-past").get("relativeTimePattern-count-other")])))


    json_dict["relative-type"]["in \\1 week"] = list(set(map(lambda x:re.sub(r'\{0\}', r'(\d+)',x) if (isinstance(x,str) or isinstance(x,unicode)) else None,
                                                [date_fields_dict.get("week").get("relativeTime-type-future").get("relativeTimePattern-count-one"),
                                                 date_fields_dict.get("week").get("relativeTime-type-future").get("relativeTimePattern-count-other"),
                                                 date_fields_dict.get("week-short").get("relativeTime-type-future").get("relativeTimePattern-count-one"),
                                                 date_fields_dict.get("week-short").get("relativeTime-type-future").get("relativeTimePattern-count-other"),
                                                 date_fields_dict.get("week-narrow").get("relativeTime-type-future").get("relativeTimePattern-count-one"),
                                                 date_fields_dict.get("week-narrow").get("relativeTime-type-future").get("relativeTimePattern-count-other")])))

    json_dict["relative-type"]["\\1 week ago"] = list(set(map(lambda x:re.sub(r'\{0\}', r'(\d+)',x) if (isinstance(x,str) or isinstance(x,unicode)) else None,
                                                [date_fields_dict.get("week").get("relativeTime-type-past").get("relativeTimePattern-count-one"),
                                                 date_fields_dict.get("week").get("relativeTime-type-past").get("relativeTimePattern-count-other"),
                                                 date_fields_dict.get("week-short").get("relativeTime-type-past").get("relativeTimePattern-count-one"),
                                                 date_fields_dict.get("week-short").get("relativeTime-type-past").get("relativeTimePattern-count-other"),
                                                 date_fields_dict.get("week-narrow").get("relativeTime-type-past").get("relativeTimePattern-count-one"),
                                                 date_fields_dict.get("week-narrow").get("relativeTime-type-past").get("relativeTimePattern-count-other")])))


    json_dict["relative-type"]["in \\1 day"] = list(set(map(lambda x:re.sub(r'\{0\}', r'(\d+)',x) if (isinstance(x,str) or isinstance(x,unicode)) else None,
                                                [date_fields_dict.get("day").get("relativeTime-type-future").get("relativeTimePattern-count-one"),
                                                 date_fields_dict.get("day").get("relativeTime-type-future").get("relativeTimePattern-count-other"),
                                                 date_fields_dict.get("day-short").get("relativeTime-type-future").get("relativeTimePattern-count-one"),
                                                 date_fields_dict.get("day-short").get("relativeTime-type-future").get("relativeTimePattern-count-other"),
                                                 date_fields_dict.get("day-narrow").get("relativeTime-type-future").get("relativeTimePattern-count-one"),
                                                 date_fields_dict.get("day-narrow").get("relativeTime-type-future").get("relativeTimePattern-count-other")])))

    json_dict["relative-type"]["\\1 day ago"] = list(set(map(lambda x:re.sub(r'\{0\}', r'(\d+)',x) if (isinstance(x,str) or isinstance(x,unicode)) else None,
                                                [date_fields_dict.get("day").get("relativeTime-type-past").get("relativeTimePattern-count-one"),
                                                 date_fields_dict.get("day").get("relativeTime-type-past").get("relativeTimePattern-count-other"),
                                                 date_fields_dict.get("day-short").get("relativeTime-type-past").get("relativeTimePattern-count-one"),
                                                 date_fields_dict.get("day-short").get("relativeTime-type-past").get("relativeTimePattern-count-other"),
                                                 date_fields_dict.get("day-narrow").get("relativeTime-type-past").get("relativeTimePattern-count-one"),
                                                 date_fields_dict.get("day-narrow").get("relativeTime-type-past").get("relativeTimePattern-count-other")])))


    json_dict["relative-type"]["in \\1 hour"] = list(set(map(lambda x:re.sub(r'\{0\}', r'(\d+)',x) if (isinstance(x,str) or isinstance(x,unicode)) else None,
                                                [date_fields_dict.get("hour").get("relativeTime-type-future").get("relativeTimePattern-count-one"),
                                                 date_fields_dict.get("hour").get("relativeTime-type-future").get("relativeTimePattern-count-other"),
                                                 date_fields_dict.get("hour-short").get("relativeTime-type-future").get("relativeTimePattern-count-one"),
                                                 date_fields_dict.get("hour-short").get("relativeTime-type-future").get("relativeTimePattern-count-other"),
                                                 date_fields_dict.get("hour-narrow").get("relativeTime-type-future").get("relativeTimePattern-count-one"),
                                                 date_fields_dict.get("hour-narrow").get("relativeTime-type-future").get("relativeTimePattern-count-other")])))

    json_dict["relative-type"]["\\1 hour ago"] = list(set(map(lambda x:re.sub(r'\{0\}', r'(\d+)',x) if (isinstance(x,str) or isinstance(x,unicode)) else None,
                                                [date_fields_dict.get("hour").get("relativeTime-type-past").get("relativeTimePattern-count-one"),
                                                 date_fields_dict.get("hour").get("relativeTime-type-past").get("relativeTimePattern-count-other"),
                                                 date_fields_dict.get("hour-short").get("relativeTime-type-past").get("relativeTimePattern-count-one"),
                                                 date_fields_dict.get("hour-short").get("relativeTime-type-past").get("relativeTimePattern-count-other"),
                                                 date_fields_dict.get("hour-narrow").get("relativeTime-type-past").get("relativeTimePattern-count-one"),
                                                 date_fields_dict.get("hour-narrow").get("relativeTime-type-past").get("relativeTimePattern-count-other")])))


    json_dict["relative-type"]["in \\1 minute"] = list(set(map(lambda x:re.sub(r'\{0\}', r'(\d+)',x) if (isinstance(x,str) or isinstance(x,unicode)) else None,
                                                [date_fields_dict.get("minute").get("relativeTime-type-future").get("relativeTimePattern-count-one"),
                                                 date_fields_dict.get("minute").get("relativeTime-type-future").get("relativeTimePattern-count-other"),
                                                 date_fields_dict.get("minute-short").get("relativeTime-type-future").get("relativeTimePattern-count-one"),
                                                 date_fields_dict.get("minute-short").get("relativeTime-type-future").get("relativeTimePattern-count-other"),
                                                 date_fields_dict.get("minute-narrow").get("relativeTime-type-future").get("relativeTimePattern-count-one"),
                                                 date_fields_dict.get("minute-narrow").get("relativeTime-type-future").get("relativeTimePattern-count-other")])))

    json_dict["relative-type"]["\\1 minute ago"] = list(set(map(lambda x:re.sub(r'\{0\}', r'(\d+)',x) if (isinstance(x,str) or isinstance(x,unicode)) else None,
                                                [date_fields_dict.get("minute").get("relativeTime-type-past").get("relativeTimePattern-count-one"),
                                                 date_fields_dict.get("minute").get("relativeTime-type-past").get("relativeTimePattern-count-other"),
                                                 date_fields_dict.get("minute-short").get("relativeTime-type-past").get("relativeTimePattern-count-one"),
                                                 date_fields_dict.get("minute-short").get("relativeTime-type-past").get("relativeTimePattern-count-other"),
                                                 date_fields_dict.get("minute-narrow").get("relativeTime-type-past").get("relativeTimePattern-count-one"),
                                                 date_fields_dict.get("minute-narrow").get("relativeTime-type-past").get("relativeTimePattern-count-other")])))


    json_dict["relative-type"]["in \\1 second"] = list(set(map(lambda x:re.sub(r'\{0\}', r'(\d+)',x) if (isinstance(x,str) or isinstance(x,unicode)) else None,
                                                [date_fields_dict.get("second").get("relativeTime-type-future").get("relativeTimePattern-count-one"),
                                                 date_fields_dict.get("second").get("relativeTime-type-future").get("relativeTimePattern-count-other"),
                                                 date_fields_dict.get("second-short").get("relativeTime-type-future").get("relativeTimePattern-count-one"),
                                                 date_fields_dict.get("second-short").get("relativeTime-type-future").get("relativeTimePattern-count-other"),
                                                 date_fields_dict.get("second-narrow").get("relativeTime-type-future").get("relativeTimePattern-count-one"),
                                                 date_fields_dict.get("second-narrow").get("relativeTime-type-future").get("relativeTimePattern-count-other")])))

    json_dict["relative-type"]["\\1 second ago"] = list(set(map(lambda x:re.sub(r'\{0\}', r'(\d+)',x) if (isinstance(x,str) or isinstance(x,unicode)) else None,
                                                [date_fields_dict.get("second").get("relativeTime-type-past").get("relativeTimePattern-count-one"),
                                                 date_fields_dict.get("second").get("relativeTime-type-past").get("relativeTimePattern-count-other"),
                                                 date_fields_dict.get("second-short").get("relativeTime-type-past").get("relativeTimePattern-count-one"),
                                                 date_fields_dict.get("second-short").get("relativeTime-type-past").get("relativeTimePattern-count-other"),
                                                 date_fields_dict.get("second-narrow").get("relativeTime-type-past").get("relativeTimePattern-count-one"),
                                                 date_fields_dict.get("second-narrow").get("relativeTime-type-past").get("relativeTimePattern-count-other")])))

    for key in json_dict["relative-type"]:
        if None in json_dict["relative-type"][key]:
            json_dict["relative-type"][key].remove(None)
    return json_dict


def get_language_locale_dict():
    while(True):
        try:
            dates_full_response = requests.get(cldr_dates_full_url, headers=headers)
        except requests.exceptions.ConnectionError:
            time.sleep(5)
            continue
        break

    if dates_full_response.status_code !=200:
        raise RuntimeError("Bad Response " + str(dates_full_response.status_code))
    dates_content = dates_full_response.json()

    available_locale_names = [locale['name'] for locale in dates_content]
    available_language_names = [locale_name for locale_name in available_locale_names if not re.search(r'-[A-Z0-9]+$',locale_name)]
    language_locale_dict = {}
    for language_name in available_language_names:
        language_locale_dict[language_name] = []
        for locale_name in available_locale_names:
            if re.match(language_name + '-[A-Z0-9]+$', locale_name):
                language_locale_dict[language_name].append(locale_name)
    return language_locale_dict

language_locale_dict = get_language_locale_dict()


def get_dict_difference(parent_dict, child_dict):
    difference_dict = OrderedDict()
    for key, value in parent_dict.items():
        child_value = child_dict[key]
        child_specific_value = None
        if isinstance(value, list):
            child_specific_value = list(set(child_value)-set(value))
        elif isinstance(value, dict):
            child_specific_value = get_dict_difference(value, child_value)
        elif child_value != value:
            child_specific_value = child_value
        if child_specific_value:
            difference_dict[key] = child_specific_value
    return difference_dict


def main():
    os.chdir(os.path.dirname(__file__))
    parent_directory = "../data/cldr_language_data"
    directory = "../data/cldr_language_data/date_translation_data"
    if not os.path.isdir(parent_directory):
        os.mkdir(parent_directory)
    if os.path.isdir(directory):
        shutil.rmtree(directory)
    os.mkdir(directory)

    for language in language_locale_dict:
        json_language_dict = retrieve_locale_data(language)
        locale_specific_dict = OrderedDict()
        locales_list = language_locale_dict[language]
        for locale in locales_list:
            json_locale_dict = retrieve_locale_data(locale)
            locale_specific_dict[locale] = get_dict_difference(json_language_dict, json_locale_dict)
        json_language_dict["locale_specific"] = locale_specific_dict
        filename = directory + '/' + language + ".json"
        print("writing " + filename)
        json_string = json.dumps(json_language_dict, indent = 4, ensure_ascii = False).encode('utf-8')
        with open(filename, 'w') as f:
            f.write(json_string)

if __name__ == '__main__':
    main()
