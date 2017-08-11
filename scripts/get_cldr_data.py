# -*- coding: utf-8 -*-
import requests
import re
import json
import os
import shutil
import time
from collections import OrderedDict
from orderedset import OrderedSet
import base64
import six

from utils import get_dict_difference
from order_languages import language_locale_dict

OAuth_Access_Token = 'OAuth_Access_Token'       # Add OAuth_Access_Token here
headers = {'Authorization': 'token %s' % OAuth_Access_Token}
cldr_dates_full_url = "https://api.github.com/repos/unicode-cldr/cldr-dates-full/contents/main/"

DATE_ORDER_PATTERN = re.compile(u'([DMY])+\u200f*[-/. \t]*([DMY])+\u200f*[-/. \t]*([DMY])+')
AVOID_RELATIVE_PATTERN = re.compile(r'[\+\-]\s*\{0\}')
AM_PATTERN = re.compile('\s*[aA]\.*\s*[mM]\.*\s*')
PM_PATTERN = re.compile('\s*[pP]\.*\s*[mM]\.*\s*')

os.chdir(os.path.dirname(os.path.abspath(__file__)))


def _modify_relative_string(relative_string):
    if isinstance(relative_string, six.string_types) and not AVOID_RELATIVE_PATTERN.search(relative_string):
        return relative_string
    else:
        return None


def _retrieve_locale_data(locale):
    cldr_gregorian_url = cldr_dates_full_url + locale + "/ca-gregorian.json?ref=master"
    cldr_datefields_url = cldr_dates_full_url + locale + "/dateFields.json?ref=master"

    while(True):
        try:
            gregorian_response = requests.get(cldr_gregorian_url, headers=headers)
        except (requests.exceptions.ConnectionError, requests.exceptions.ChunkedEncodingError):
            print("Waiting...")
            time.sleep(5)
        else:
            break

    if gregorian_response.status_code != 200:
        raise RuntimeError("Bad Response " + str(gregorian_response.status_code))
    gregorian_content = base64.b64decode(gregorian_response.json()["content"]).decode("utf-8")
    cldr_gregorian_data = json.loads(gregorian_content)
    json_dict = OrderedDict()
    gregorian_dict = cldr_gregorian_data["main"][locale]["dates"]["calendars"]["gregorian"]

    while(True):
        try:
            datefields_response = requests.get(cldr_datefields_url, headers=headers)
        except (requests.exceptions.ConnectionError, requests.exceptions.ChunkedEncodingError):
            print("Waiting...")
            time.sleep(5)
        else:
            break

    if datefields_response.status_code != 200:
        raise RuntimeError("Bad Response " + str(datefields_response.status_code))
    datefields_content = base64.b64decode(datefields_response.json()["content"]).decode("utf-8")
    cldr_datefields_data = json.loads(datefields_content)

    date_fields_dict = cldr_datefields_data["main"][locale]["dates"]["fields"]

    json_dict["name"] = locale

    try:
        date_format_string = gregorian_dict["dateFormats"]["short"].upper()
    except:
        date_format_string = gregorian_dict["dateFormats"]["short"]["_value"].upper()

    json_dict["date_order"] = DATE_ORDER_PATTERN.sub(
            r'\1\2\3', DATE_ORDER_PATTERN.search(date_format_string).group())

    json_dict["january"] = [gregorian_dict["months"]["stand-alone"]["wide"]["1"],
                            gregorian_dict["months"]["stand-alone"]["abbreviated"]["1"],
                            gregorian_dict["months"]["stand-alone"]["narrow"]["1"],
                            gregorian_dict["months"]["format"]["wide"]["1"],
                            gregorian_dict["months"]["format"]["abbreviated"]["1"],
                            gregorian_dict["months"]["format"]["narrow"]["1"]]

    json_dict["february"] = [gregorian_dict["months"]["stand-alone"]["wide"]["2"],
                             gregorian_dict["months"]["stand-alone"]["abbreviated"]["2"],
                             gregorian_dict["months"]["stand-alone"]["narrow"]["2"],
                             gregorian_dict["months"]["format"]["wide"]["2"],
                             gregorian_dict["months"]["format"]["abbreviated"]["2"],
                             gregorian_dict["months"]["format"]["narrow"]["2"]]

    json_dict["march"] = [gregorian_dict["months"]["stand-alone"]["wide"]["3"],
                          gregorian_dict["months"]["stand-alone"]["abbreviated"]["3"],
                          gregorian_dict["months"]["stand-alone"]["narrow"]["3"],
                          gregorian_dict["months"]["format"]["wide"]["3"],
                          gregorian_dict["months"]["format"]["abbreviated"]["3"],
                          gregorian_dict["months"]["format"]["narrow"]["3"]]

    json_dict["april"] = [gregorian_dict["months"]["stand-alone"]["wide"]["4"],
                          gregorian_dict["months"]["stand-alone"]["abbreviated"]["4"],
                          gregorian_dict["months"]["stand-alone"]["narrow"]["4"],
                          gregorian_dict["months"]["format"]["wide"]["4"],
                          gregorian_dict["months"]["format"]["abbreviated"]["4"],
                          gregorian_dict["months"]["format"]["narrow"]["4"]]

    json_dict["may"] = [gregorian_dict["months"]["stand-alone"]["wide"]["5"],
                        gregorian_dict["months"]["stand-alone"]["abbreviated"]["5"],
                        gregorian_dict["months"]["stand-alone"]["narrow"]["5"],
                        gregorian_dict["months"]["format"]["wide"]["5"],
                        gregorian_dict["months"]["format"]["abbreviated"]["5"],
                        gregorian_dict["months"]["format"]["narrow"]["5"]]

    json_dict["june"] = [gregorian_dict["months"]["stand-alone"]["wide"]["6"],
                         gregorian_dict["months"]["stand-alone"]["abbreviated"]["6"],
                         gregorian_dict["months"]["stand-alone"]["narrow"]["6"],
                         gregorian_dict["months"]["format"]["wide"]["6"],
                         gregorian_dict["months"]["format"]["abbreviated"]["6"],
                         gregorian_dict["months"]["format"]["narrow"]["6"]]

    json_dict["july"] = [gregorian_dict["months"]["stand-alone"]["wide"]["7"],
                         gregorian_dict["months"]["stand-alone"]["abbreviated"]["7"],
                         gregorian_dict["months"]["stand-alone"]["narrow"]["7"],
                         gregorian_dict["months"]["format"]["wide"]["7"],
                         gregorian_dict["months"]["format"]["abbreviated"]["7"],
                         gregorian_dict["months"]["format"]["narrow"]["7"]]

    json_dict["august"] = [gregorian_dict["months"]["stand-alone"]["wide"]["8"],
                           gregorian_dict["months"]["stand-alone"]["abbreviated"]["8"],
                           gregorian_dict["months"]["stand-alone"]["narrow"]["8"],
                           gregorian_dict["months"]["format"]["wide"]["8"],
                           gregorian_dict["months"]["format"]["abbreviated"]["8"],
                           gregorian_dict["months"]["format"]["narrow"]["8"]]

    json_dict["september"] = [gregorian_dict["months"]["stand-alone"]["wide"]["9"],
                              gregorian_dict["months"]["stand-alone"]["abbreviated"]["9"],
                              gregorian_dict["months"]["stand-alone"]["narrow"]["9"],
                              gregorian_dict["months"]["format"]["wide"]["9"],
                              gregorian_dict["months"]["format"]["abbreviated"]["9"],
                              gregorian_dict["months"]["format"]["narrow"]["9"]]

    json_dict["october"] = [gregorian_dict["months"]["stand-alone"]["wide"]["10"],
                            gregorian_dict["months"]["stand-alone"]["abbreviated"]["10"],
                            gregorian_dict["months"]["stand-alone"]["narrow"]["10"],
                            gregorian_dict["months"]["format"]["wide"]["10"],
                            gregorian_dict["months"]["format"]["abbreviated"]["10"],
                            gregorian_dict["months"]["format"]["narrow"]["10"]]

    json_dict["november"] = [gregorian_dict["months"]["stand-alone"]["wide"]["11"],
                             gregorian_dict["months"]["stand-alone"]["abbreviated"]["11"],
                             gregorian_dict["months"]["stand-alone"]["narrow"]["11"],
                             gregorian_dict["months"]["format"]["wide"]["11"],
                             gregorian_dict["months"]["format"]["abbreviated"]["11"],
                             gregorian_dict["months"]["format"]["narrow"]["11"]]

    json_dict["december"] = [gregorian_dict["months"]["stand-alone"]["wide"]["12"],
                             gregorian_dict["months"]["stand-alone"]["abbreviated"]["12"],
                             gregorian_dict["months"]["stand-alone"]["narrow"]["12"],
                             gregorian_dict["months"]["format"]["wide"]["12"],
                             gregorian_dict["months"]["format"]["abbreviated"]["12"],
                             gregorian_dict["months"]["format"]["narrow"]["12"]]

    json_dict["monday"] = [gregorian_dict["days"]["stand-alone"]["wide"]["mon"],
                           gregorian_dict["days"]["stand-alone"]["abbreviated"]["mon"],
                           gregorian_dict["days"]["stand-alone"]["narrow"]["mon"],
                           gregorian_dict["days"]["format"]["wide"]["mon"],
                           gregorian_dict["days"]["format"]["abbreviated"]["mon"],
                           gregorian_dict["days"]["format"]["narrow"]["mon"]]

    json_dict["tuesday"] = [gregorian_dict["days"]["stand-alone"]["wide"]["tue"],
                            gregorian_dict["days"]["stand-alone"]["abbreviated"]["tue"],
                            gregorian_dict["days"]["stand-alone"]["narrow"]["tue"],
                            gregorian_dict["days"]["format"]["wide"]["tue"],
                            gregorian_dict["days"]["format"]["abbreviated"]["tue"],
                            gregorian_dict["days"]["format"]["narrow"]["tue"]]

    json_dict["wednesday"] = [gregorian_dict["days"]["stand-alone"]["wide"]["wed"],
                              gregorian_dict["days"]["stand-alone"]["abbreviated"]["wed"],
                              gregorian_dict["days"]["stand-alone"]["narrow"]["wed"],
                              gregorian_dict["days"]["format"]["wide"]["wed"],
                              gregorian_dict["days"]["format"]["abbreviated"]["wed"],
                              gregorian_dict["days"]["format"]["narrow"]["wed"]]

    json_dict["thursday"] = [gregorian_dict["days"]["stand-alone"]["wide"]["thu"],
                             gregorian_dict["days"]["stand-alone"]["abbreviated"]["thu"],
                             gregorian_dict["days"]["stand-alone"]["narrow"]["thu"],
                             gregorian_dict["days"]["format"]["wide"]["thu"],
                             gregorian_dict["days"]["format"]["abbreviated"]["thu"],
                             gregorian_dict["days"]["format"]["narrow"]["thu"]]

    json_dict["friday"] = [gregorian_dict["days"]["stand-alone"]["wide"]["fri"],
                           gregorian_dict["days"]["stand-alone"]["abbreviated"]["fri"],
                           gregorian_dict["days"]["stand-alone"]["narrow"]["fri"],
                           gregorian_dict["days"]["format"]["wide"]["fri"],
                           gregorian_dict["days"]["format"]["abbreviated"]["fri"],
                           gregorian_dict["days"]["format"]["narrow"]["fri"]]

    json_dict["saturday"] = [gregorian_dict["days"]["stand-alone"]["wide"]["sat"],
                             gregorian_dict["days"]["stand-alone"]["abbreviated"]["sat"],
                             gregorian_dict["days"]["stand-alone"]["narrow"]["sat"],
                             gregorian_dict["days"]["format"]["wide"]["sat"],
                             gregorian_dict["days"]["format"]["abbreviated"]["sat"],
                             gregorian_dict["days"]["format"]["narrow"]["sat"]]

    json_dict["sunday"] = [gregorian_dict["days"]["stand-alone"]["wide"]["sun"],
                           gregorian_dict["days"]["stand-alone"]["abbreviated"]["sun"],
                           gregorian_dict["days"]["stand-alone"]["narrow"]["sun"],
                           gregorian_dict["days"]["format"]["wide"]["sun"],
                           gregorian_dict["days"]["format"]["abbreviated"]["sun"],
                           gregorian_dict["days"]["format"]["narrow"]["sun"]]

    json_dict["am"] = list(AM_PATTERN.sub('am', x) for x in
                           [gregorian_dict["dayPeriods"]["stand-alone"]["wide"]["am"],
                            gregorian_dict["dayPeriods"]["stand-alone"]["abbreviated"]["am"],
                            gregorian_dict["dayPeriods"]["stand-alone"]["narrow"]["am"],
                            gregorian_dict["dayPeriods"]["format"]["wide"]["am"],
                            gregorian_dict["dayPeriods"]["format"]["abbreviated"]["am"],
                            gregorian_dict["dayPeriods"]["format"]["narrow"]["am"]])

    json_dict["pm"] = list(PM_PATTERN.sub('pm', x) for x in
                           [gregorian_dict["dayPeriods"]["stand-alone"]["wide"]["pm"],
                            gregorian_dict["dayPeriods"]["stand-alone"]["abbreviated"]["pm"],
                            gregorian_dict["dayPeriods"]["stand-alone"]["narrow"]["pm"],
                            gregorian_dict["dayPeriods"]["format"]["wide"]["pm"],
                            gregorian_dict["dayPeriods"]["format"]["abbreviated"]["pm"],
                            gregorian_dict["dayPeriods"]["format"]["narrow"]["pm"]])

    json_dict["year"] = [date_fields_dict["year"]["displayName"],
                         date_fields_dict["year-short"]["displayName"],
                         date_fields_dict["year-narrow"]["displayName"]]

    json_dict["month"] = [date_fields_dict["month"]["displayName"],
                          date_fields_dict["month-short"]["displayName"],
                          date_fields_dict["month-narrow"]["displayName"]]

    json_dict["week"] = [date_fields_dict["week"]["displayName"],
                         date_fields_dict["week-short"]["displayName"],
                         date_fields_dict["week-narrow"]["displayName"]]

    json_dict["day"] = [date_fields_dict["day"]["displayName"],
                        date_fields_dict["day-short"]["displayName"],
                        date_fields_dict["day-narrow"]["displayName"]]

    json_dict["hour"] = [date_fields_dict["hour"]["displayName"],
                         date_fields_dict["hour-short"]["displayName"],
                         date_fields_dict["hour-narrow"]["displayName"]]

    json_dict["minute"] = [date_fields_dict["minute"]["displayName"],
                           date_fields_dict["minute-short"]["displayName"],
                           date_fields_dict["minute-narrow"]["displayName"]]

    json_dict["second"] = [date_fields_dict["second"]["displayName"],
                           date_fields_dict["second-short"]["displayName"],
                           date_fields_dict["second-narrow"]["displayName"]]

    json_dict["relative-type"] = OrderedDict()

    json_dict["relative-type"]["1 year ago"] = [date_fields_dict["year"]["relative-type--1"],
                                                date_fields_dict["year-short"]["relative-type--1"],
                                                date_fields_dict["year-narrow"]["relative-type--1"]]

    json_dict["relative-type"]["0 year ago"] = [date_fields_dict["year"]["relative-type-0"],
                                                date_fields_dict["year-short"]["relative-type-0"],
                                                date_fields_dict["year-narrow"]["relative-type-0"]]

    json_dict["relative-type"]["in 1 year"] = [date_fields_dict["year"]["relative-type-1"],
                                               date_fields_dict["year-short"]["relative-type-1"],
                                               date_fields_dict["year-narrow"]["relative-type-1"]]

    json_dict["relative-type"]["1 month ago"] = [date_fields_dict["month"]["relative-type--1"],
                                                 date_fields_dict["month-short"]["relative-type--1"],
                                                 date_fields_dict["month-narrow"]["relative-type--1"]]

    json_dict["relative-type"]["0 month ago"] = [date_fields_dict["month"]["relative-type-0"],
                                                 date_fields_dict["month-short"]["relative-type-0"],
                                                 date_fields_dict["month-narrow"]["relative-type-0"]]

    json_dict["relative-type"]["in 1 month"] = [date_fields_dict["month"]["relative-type-1"],
                                                date_fields_dict["month-short"]["relative-type-1"],
                                                date_fields_dict["month-narrow"]["relative-type-1"]]

    json_dict["relative-type"]["1 week ago"] = [date_fields_dict["week"]["relative-type--1"],
                                                date_fields_dict["week-short"]["relative-type--1"],
                                                date_fields_dict["week-narrow"]["relative-type--1"]]

    json_dict["relative-type"]["0 week ago"] = [date_fields_dict["week"]["relative-type-0"],
                                                date_fields_dict["week-short"]["relative-type-0"],
                                                date_fields_dict["week-narrow"]["relative-type-0"]]

    json_dict["relative-type"]["in 1 week"] = [date_fields_dict["week"]["relative-type-1"],
                                               date_fields_dict["week-short"]["relative-type-1"],
                                               date_fields_dict["week-narrow"]["relative-type-1"]]

    json_dict["relative-type"]["1 day ago"] = [date_fields_dict["day"]["relative-type--1"],
                                               date_fields_dict["day-short"]["relative-type--1"],
                                               date_fields_dict["day-narrow"]["relative-type--1"]]

    json_dict["relative-type"]["0 day ago"] = [date_fields_dict["day"]["relative-type-0"],
                                               date_fields_dict["day-short"]["relative-type-0"],
                                               date_fields_dict["day-narrow"]["relative-type-0"]]

    json_dict["relative-type"]["in 1 day"] = [date_fields_dict["day"]["relative-type-1"],
                                              date_fields_dict["day-short"]["relative-type-1"],
                                              date_fields_dict["day-narrow"]["relative-type-1"]]

    json_dict["relative-type"]["0 hour ago"] = [date_fields_dict["hour"]["relative-type-0"],
                                                date_fields_dict["hour-short"]["relative-type-0"],
                                                date_fields_dict["hour-narrow"]["relative-type-0"]]

    json_dict["relative-type"]["0 minute ago"] = [date_fields_dict["minute"]["relative-type-0"],
                                                  date_fields_dict["minute-short"]["relative-type-0"],
                                                  date_fields_dict["minute-narrow"]["relative-type-0"]]

    json_dict["relative-type"]["0 second ago"] = [date_fields_dict["second"]["relative-type-0"],
                                                  date_fields_dict["second-short"]["relative-type-0"],
                                                  date_fields_dict["second-narrow"]["relative-type-0"]]

    json_dict["relative-type-regex"] = OrderedDict()

    json_dict["relative-type-regex"]["in \\1 year"] = (
        list(map(_modify_relative_string,
                 [date_fields_dict["year"]["relativeTime-type-future"].get("relativeTimePattern-count-one"),
                  date_fields_dict["year"]["relativeTime-type-future"].get("relativeTimePattern-count-other"),
                  date_fields_dict["year-short"]["relativeTime-type-future"].get("relativeTimePattern-count-one"),
                  date_fields_dict["year-short"]["relativeTime-type-future"].get("relativeTimePattern-count-other"),
                  date_fields_dict["year-narrow"]["relativeTime-type-future"].get("relativeTimePattern-count-one"),
                  date_fields_dict["year-narrow"]["relativeTime-type-future"].get("relativeTimePattern-count-other")])))

    json_dict["relative-type-regex"]["\\1 year ago"] = (
        list(map(_modify_relative_string,
                 [date_fields_dict["year"]["relativeTime-type-past"].get("relativeTimePattern-count-one"),
                  date_fields_dict["year"]["relativeTime-type-past"].get("relativeTimePattern-count-other"),
                  date_fields_dict["year-short"]["relativeTime-type-past"].get("relativeTimePattern-count-one"),
                  date_fields_dict["year-short"]["relativeTime-type-past"].get("relativeTimePattern-count-other"),
                  date_fields_dict["year-narrow"]["relativeTime-type-past"].get("relativeTimePattern-count-one"),
                  date_fields_dict["year-narrow"]["relativeTime-type-past"].get("relativeTimePattern-count-other")])))

    json_dict["relative-type-regex"]["in \\1 month"] = (
        list(map(_modify_relative_string,
                 [date_fields_dict["month"]["relativeTime-type-future"].get("relativeTimePattern-count-one"),
                  date_fields_dict["month"]["relativeTime-type-future"].get("relativeTimePattern-count-other"),
                  date_fields_dict["month-short"]["relativeTime-type-future"].get("relativeTimePattern-count-one"),
                  date_fields_dict["month-short"]["relativeTime-type-future"].get("relativeTimePattern-count-other"),
                  date_fields_dict["month-narrow"]["relativeTime-type-future"].get("relativeTimePattern-count-one"),
                  date_fields_dict["month-narrow"]["relativeTime-type-future"].get("relativeTimePattern-count-other")])))

    json_dict["relative-type-regex"]["\\1 month ago"] = (
        list(map(_modify_relative_string,
                 [date_fields_dict["month"]["relativeTime-type-past"].get("relativeTimePattern-count-one"),
                  date_fields_dict["month"]["relativeTime-type-past"].get("relativeTimePattern-count-other"),
                  date_fields_dict["month-short"]["relativeTime-type-past"].get("relativeTimePattern-count-one"),
                  date_fields_dict["month-short"]["relativeTime-type-past"].get("relativeTimePattern-count-other"),
                  date_fields_dict["month-narrow"]["relativeTime-type-past"].get("relativeTimePattern-count-one"),
                  date_fields_dict["month-narrow"]["relativeTime-type-past"].get("relativeTimePattern-count-other")])))

    json_dict["relative-type-regex"]["in \\1 week"] = (
        list(map(_modify_relative_string,
                 [date_fields_dict["week"]["relativeTime-type-future"].get("relativeTimePattern-count-one"),
                  date_fields_dict["week"]["relativeTime-type-future"].get("relativeTimePattern-count-other"),
                  date_fields_dict["week-short"]["relativeTime-type-future"].get("relativeTimePattern-count-one"),
                  date_fields_dict["week-short"]["relativeTime-type-future"].get("relativeTimePattern-count-other"),
                  date_fields_dict["week-narrow"]["relativeTime-type-future"].get("relativeTimePattern-count-one"),
                  date_fields_dict["week-narrow"]["relativeTime-type-future"].get("relativeTimePattern-count-other")])))

    json_dict["relative-type-regex"]["\\1 week ago"] = (
        list(map(_modify_relative_string,
                 [date_fields_dict["week"]["relativeTime-type-past"].get("relativeTimePattern-count-one"),
                  date_fields_dict["week"]["relativeTime-type-past"].get("relativeTimePattern-count-other"),
                  date_fields_dict["week-short"]["relativeTime-type-past"].get("relativeTimePattern-count-one"),
                  date_fields_dict["week-short"]["relativeTime-type-past"].get("relativeTimePattern-count-other"),
                  date_fields_dict["week-narrow"]["relativeTime-type-past"].get("relativeTimePattern-count-one"),
                  date_fields_dict["week-narrow"]["relativeTime-type-past"].get("relativeTimePattern-count-other")])))

    json_dict["relative-type-regex"]["in \\1 day"] = (
        list(map(_modify_relative_string,
                 [date_fields_dict["day"]["relativeTime-type-future"].get("relativeTimePattern-count-one"),
                  date_fields_dict["day"]["relativeTime-type-future"].get("relativeTimePattern-count-other"),
                  date_fields_dict["day-short"]["relativeTime-type-future"].get("relativeTimePattern-count-one"),
                  date_fields_dict["day-short"]["relativeTime-type-future"].get("relativeTimePattern-count-other"),
                  date_fields_dict["day-narrow"]["relativeTime-type-future"].get("relativeTimePattern-count-one"),
                  date_fields_dict["day-narrow"]["relativeTime-type-future"].get("relativeTimePattern-count-other")])))

    json_dict["relative-type-regex"]["\\1 day ago"] = (
        list(map(_modify_relative_string,
                 [date_fields_dict["day"]["relativeTime-type-past"].get("relativeTimePattern-count-one"),
                  date_fields_dict["day"]["relativeTime-type-past"].get("relativeTimePattern-count-other"),
                  date_fields_dict["day-short"]["relativeTime-type-past"].get("relativeTimePattern-count-one"),
                  date_fields_dict["day-short"]["relativeTime-type-past"].get("relativeTimePattern-count-other"),
                  date_fields_dict["day-narrow"]["relativeTime-type-past"].get("relativeTimePattern-count-one"),
                  date_fields_dict["day-narrow"]["relativeTime-type-past"].get("relativeTimePattern-count-other")])))

    json_dict["relative-type-regex"]["in \\1 hour"] = (
        list(map(_modify_relative_string,
                 [date_fields_dict["hour"]["relativeTime-type-future"].get("relativeTimePattern-count-one"),
                  date_fields_dict["hour"]["relativeTime-type-future"].get("relativeTimePattern-count-other"),
                  date_fields_dict["hour-short"]["relativeTime-type-future"].get("relativeTimePattern-count-one"),
                  date_fields_dict["hour-short"]["relativeTime-type-future"].get("relativeTimePattern-count-other"),
                  date_fields_dict["hour-narrow"]["relativeTime-type-future"].get("relativeTimePattern-count-one"),
                  date_fields_dict["hour-narrow"]["relativeTime-type-future"].get("relativeTimePattern-count-other")])))

    json_dict["relative-type-regex"]["\\1 hour ago"] = (
        list(map(_modify_relative_string,
                 [date_fields_dict["hour"]["relativeTime-type-past"].get("relativeTimePattern-count-one"),
                  date_fields_dict["hour"]["relativeTime-type-past"].get("relativeTimePattern-count-other"),
                  date_fields_dict["hour-short"]["relativeTime-type-past"].get("relativeTimePattern-count-one"),
                  date_fields_dict["hour-short"]["relativeTime-type-past"].get("relativeTimePattern-count-other"),
                  date_fields_dict["hour-narrow"]["relativeTime-type-past"].get("relativeTimePattern-count-one"),
                  date_fields_dict["hour-narrow"]["relativeTime-type-past"].get("relativeTimePattern-count-other")])))

    json_dict["relative-type-regex"]["in \\1 minute"] = (
        list(map(_modify_relative_string,
                 [date_fields_dict["minute"]["relativeTime-type-future"].get("relativeTimePattern-count-one"),
                  date_fields_dict["minute"]["relativeTime-type-future"].get("relativeTimePattern-count-other"),
                  date_fields_dict["minute-short"]["relativeTime-type-future"].get("relativeTimePattern-count-one"),
                  date_fields_dict["minute-short"]["relativeTime-type-future"].get("relativeTimePattern-count-other"),
                  date_fields_dict["minute-narrow"]["relativeTime-type-future"].get("relativeTimePattern-count-one"),
                  date_fields_dict["minute-narrow"]["relativeTime-type-future"].get("relativeTimePattern-count-other")])))

    json_dict["relative-type-regex"]["\\1 minute ago"] = (
        list(map(_modify_relative_string,
                 [date_fields_dict["minute"]["relativeTime-type-past"].get("relativeTimePattern-count-one"),
                  date_fields_dict["minute"]["relativeTime-type-past"].get("relativeTimePattern-count-other"),
                  date_fields_dict["minute-short"]["relativeTime-type-past"].get("relativeTimePattern-count-one"),
                  date_fields_dict["minute-short"]["relativeTime-type-past"].get("relativeTimePattern-count-other"),
                  date_fields_dict["minute-narrow"]["relativeTime-type-past"].get("relativeTimePattern-count-one"),
                  date_fields_dict["minute-narrow"]["relativeTime-type-past"].get("relativeTimePattern-count-other")])))

    json_dict["relative-type-regex"]["in \\1 second"] = (
        list(map(_modify_relative_string,
                 [date_fields_dict["second"]["relativeTime-type-future"].get("relativeTimePattern-count-one"),
                  date_fields_dict["second"]["relativeTime-type-future"].get("relativeTimePattern-count-other"),
                  date_fields_dict["second-short"]["relativeTime-type-future"].get("relativeTimePattern-count-one"),
                  date_fields_dict["second-short"]["relativeTime-type-future"].get("relativeTimePattern-count-other"),
                  date_fields_dict["second-narrow"]["relativeTime-type-future"].get("relativeTimePattern-count-one"),
                  date_fields_dict["second-narrow"]["relativeTime-type-future"].get("relativeTimePattern-count-other")])))

    json_dict["relative-type-regex"]["\\1 second ago"] = (
        list(map(_modify_relative_string,
                 [date_fields_dict["second"]["relativeTime-type-past"].get("relativeTimePattern-count-one"),
                  date_fields_dict["second"]["relativeTime-type-past"].get("relativeTimePattern-count-other"),
                  date_fields_dict["second-short"]["relativeTime-type-past"].get("relativeTimePattern-count-one"),
                  date_fields_dict["second-short"]["relativeTime-type-past"].get("relativeTimePattern-count-other"),
                  date_fields_dict["second-narrow"]["relativeTime-type-past"].get("relativeTimePattern-count-one"),
                  date_fields_dict["second-narrow"]["relativeTime-type-past"].get("relativeTimePattern-count-other")])))

    return json_dict


def _clean_dict(json_dict):
    redundant_keys = []
    for key, value in json_dict.items():
        if not value:
            redundant_keys.append(key)
        elif isinstance(value, list):
            value = [i for i in value if isinstance(i, six.string_types) and not i.isdigit()]
            if not value:
                redundant_keys.append(key)
            else:
                json_dict[key] = list(OrderedSet(map(
                    lambda y: ' '.join(list(map(lambda x: x.rstrip('.'), y.lower().split()))), value)))
        elif isinstance(value, dict):
            json_dict[key] = _clean_dict(value)

    for key in redundant_keys:
        del json_dict[key]
    return json_dict


def main():
    parent_directory = "../data/cldr_language_data"
    directory = "../data/cldr_language_data/date_translation_data/"
    if not os.path.isdir(parent_directory):
        os.mkdir(parent_directory)
    if os.path.isdir(directory):
        shutil.rmtree(directory)
    os.mkdir(directory)

    for language in language_locale_dict:
        json_language_dict = _clean_dict(_retrieve_locale_data(language))
        locale_specific_dict = OrderedDict()
        locales_list = language_locale_dict[language]
        for locale in locales_list:
            json_locale_dict = _clean_dict(_retrieve_locale_data(locale))
            locale_specific_dict[locale] = get_dict_difference(json_language_dict, json_locale_dict)
        json_language_dict["locale_specific"] = locale_specific_dict
        filename = directory + language + ".json"
        print("writing " + filename)
        json_string = json.dumps(json_language_dict, indent=4, separators=(',', ': '),
                                 ensure_ascii=False).encode('utf-8')
        with open(filename, 'wb') as f:
            f.write(json_string)


if __name__ == '__main__':
    main()
