import sys

from tzlocal import get_localzone
from datetime import timezone

from .timezone_parser import pop_tz_offset_from_string
from .utils import strip_braces, apply_timezone, localize_timezone
from .conf import apply_settings


class DateParser:

    @apply_settings
    def parse(self, date_string, parse_method, settings=None):
        date_string = str(date_string)

        if not date_string.strip():
            raise ValueError("Empty string")

        date_string = strip_braces(date_string)
        date_string, ptz = pop_tz_offset_from_string(date_string)

        date_obj, period = parse_method(date_string, settings=settings, tz=ptz)

        if ptz:
            if hasattr(ptz, "localize"):
                date_obj = ptz.localize(date_obj)
            else:
                date_obj = date_obj.replace(tzinfo=ptz)
            if isinstance(settings.TIMEZONE, timezone):
                date_obj = date_obj.astimezone(settings.TIMEZONE)
            elif "local" not in settings.TIMEZONE:
                date_obj = apply_timezone(date_obj, settings.TIMEZONE)
        elif isinstance(settings.TIMEZONE, timezone):
            date_obj = date_obj.astimezone(settings.TIMEZONE)
        elif "local" in settings.TIMEZONE:
            stz = get_localzone()
            if hasattr(stz, "localize") and sys.version_info < (3, 6):
                date_obj = stz.localize(date_obj)
            else:
                date_obj = date_obj.replace(tzinfo=stz)
        else:
            date_obj = localize_timezone(date_obj, settings.TIMEZONE)

        if isinstance(settings.TO_TIMEZONE, timezone):
            date_obj = date_obj.replace(tzinfo=settings.TO_TIMEZONE)
        elif settings.TO_TIMEZONE:
            date_obj = apply_timezone(date_obj, settings.TO_TIMEZONE)

        if (
            not settings.RETURN_AS_TIMEZONE_AWARE
            or (settings.RETURN_AS_TIMEZONE_AWARE
                and 'default' == settings.RETURN_AS_TIMEZONE_AWARE and not ptz)
        ):
            date_obj = date_obj.replace(tzinfo=None)

        return date_obj, period


date_parser = DateParser()
