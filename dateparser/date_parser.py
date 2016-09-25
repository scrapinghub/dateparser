# coding: utf-8
from __future__ import unicode_literals

import six

from tzlocal import get_localzone

from .timezone_parser import pop_tz_offset_from_string
from .utils import strip_braces, apply_timezone, localize_timezone
from .conf import apply_settings
from .parser import parse


class DateParser(object):

    @apply_settings
    def parse(self, date_string, settings=None):
        date_string = six.text_type(date_string)

        if not date_string.strip():
            raise ValueError("Empty string")

        date_string = strip_braces(date_string)
        date_string, ptz = pop_tz_offset_from_string(date_string)

        date_obj, period = parse(date_string, settings=settings)

        if ptz is not None:
            date_obj = ptz.localize(date_obj)
        elif 'local' in settings.TIMEZONE.lower():
            stz = get_localzone()
            date_obj = stz.localize(date_obj)
        else:
            date_obj = localize_timezone(date_obj, settings.TIMEZONE)

        if settings.TO_TIMEZONE:
            date_obj = apply_timezone(date_obj, settings.TO_TIMEZONE)

        if not settings.RETURN_AS_TIMEZONE_AWARE or ptz is None:
            date_obj = date_obj.replace(tzinfo=None)

        return date_obj, period


date_parser = DateParser()
