# coding: utf-8
from __future__ import unicode_literals

import six

from .timezone_parser import pop_tz_offset_from_string
from .utils import strip_braces, apply_timezone
from .conf import apply_settings
from .parser import parse


class DateParser(object):

    @apply_settings
    def parse(self, date_string, settings=None):
        date_string = six.text_type(date_string)

        if not date_string.strip():
            raise ValueError("Empty string")

        date_string = strip_braces(date_string)
        date_string, tz = pop_tz_offset_from_string(date_string)

        date_obj, period = parse(date_string, settings=settings)

        if tz is not None:
            date_obj = tz.localize(date_obj)

        if settings.TIMEZONE:
            date_obj = apply_timezone(date_obj, settings.TIMEZONE)

        if not settings.RETURN_AS_TIMEZONE_AWARE:
            date_obj = date_obj.replace(tzinfo=None)

        return date_obj, period


date_parser = DateParser()
