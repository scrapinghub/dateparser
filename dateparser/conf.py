# -*- coding: utf-8 -*-
import hashlib
from datetime import datetime
from functools import wraps
import six

from .utils import registry


@registry
class Settings(object):
    """Control and configure default parsing behavior of dateparser.
    Currently, supported settings are:

    * `PREFER_DATES_FROM`: defaults to `current_period`. Options are `future` or `past`.
    * `PREFER_DAY_OF_MONTH`: defaults to `current`. Could be `first` and `last` day of month.
    * `SKIP_TOKENS`: defaults to `['t']`. Can be any string.
    * `TIMEZONE`: defaults to `UTC`. Can be timezone abbreviation or any of `tz database name as given here <https://en.wikipedia.org/wiki/List_of_tz_database_time_zones>`_.
    * `RETURN_AS_TIMEZONE_AWARE`: return tz aware datetime objects in case timezone is detected in the date string.
    * `RELATIVE_BASE`: count relative date from this base date. Should be datetime object.
    * `RETURN_TIME_AS_PERIOD`: returns period as `time` in case time component is detected in the date string.
    Default: False.
    * `PARSERS`: list of date parsers to use, in order of preference. Default:
    :attr:`dateparser.settings.default_parsers`.
    """

    _default = True
    _pyfile_data = None
    _mod_settings = dict()

    def __init__(self, settings=None):
        if settings:
            self._updateall(settings.items())
        else:
            self._updateall(self._get_settings_from_pyfile().items())

    @classmethod
    def get_key(cls, settings=None):
        if not settings:
            return 'default'

        keys = sorted(['%s-%s' % (key, str(settings[key])) for key in settings])
        return hashlib.md5(''.join(keys).encode('utf-8')).hexdigest()

    @classmethod
    def _get_settings_from_pyfile(cls):
        if not cls._pyfile_data:
            from dateparser_data import settings

            cls._pyfile_data = settings.settings
        return cls._pyfile_data

    def _updateall(self, iterable):
        for key, value in iterable:
            setattr(self, key, value)

    def replace(self, mod_settings=None, **kwds):
        for k, v in six.iteritems(kwds):
            if v is None:
                raise TypeError('Invalid {{"{}": {}}}'.format(k, v))

        for x in six.iterkeys(self._get_settings_from_pyfile()):
            kwds.setdefault(x, getattr(self, x))

        kwds['_default'] = False
        if mod_settings:
            kwds['_mod_settings'] = mod_settings

        return self.__class__(settings=kwds)


settings = Settings()


def apply_settings(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        mod_settings = kwargs.get('settings')
        kwargs['settings'] = mod_settings or settings

        if isinstance(kwargs['settings'], dict):
            kwargs['settings'] = settings.replace(
                mod_settings=mod_settings, **kwargs['settings']
            )

        if not isinstance(kwargs['settings'], Settings):
            raise TypeError(
                "settings can only be either dict or instance of Settings class"
            )

        return f(*args, **kwargs)

    return wrapper


class SettingValidationError(ValueError):
    pass


def check_settings(settings):
    # move this checks to be performed inside DateDataParser constructor??

    settings_values = {
        # Date order
        'DATE_ORDER': {
            'values': ('MDY', 'MYD', 'DMY', 'DYM', 'YDM', 'YMD'),
            # TODO: extract from parser.py --> resolve_date_order --> chart?
            'type': str,
        },

        # Timezone related
        'TIMEZONE': {
            'values': (),  # undetermined number of valid values  # TODO: Should we check invalid strings in anywhere in the code?
            'type': str,
        },
        'TO_TIMEZONE': {
            # defaults to None. When specified, resultant :class:`datetime <datetime.datetime>` converts according to the supplied timezone:
            'values': (True, False),  # TODO: change!
            'type': bool  # TODO: change!
        },

        #     'RETURN_AS_TIMEZONE_AWARE': 'default',  # should be True/False but they needed to check if it was per default [_mod_settings ]


        # INCOMPLETE DATES
        'PREFER_DAY_OF_MONTH': {
            'values': ('current', 'first', 'last'),
            'type': str
        },
        'PREFER_DATES_FROM': {
            'values': ('current_period', 'past', 'future'),
            'type': str,
        },
        'RELATIVE_BASE': {
            'values': (),  # undetermined number of valid values  # TODO: Should we check invalid strings in anywhere in the code?
            'type': datetime
        },
        'STRICT_PARSING': {
            'values': (True, False),
            'type': bool
        },
        # 'REQUIRE_PARTS': [],

        # Language detection
        # 'SKIP_TOKENS': ["t"],
        'NORMALIZE': {
            'values': (True, False),
            'type': bool
        },

        # Other settings
        'RETURN_TIME_AS_PERIOD': {
            'values': (True, False),
            'type': bool
        },

        #     'PARSERS': default_parsers,


        # Not documented

        #     'SKIP_TOKENS_PARSER': ["t", "year", "hour", "minute"],

        'FUZZY': {
            'values': (True, False),
            'type': bool
        },
        'PREFER_LOCALE_DATE_ORDER': {
            'values': (True, False),
            'type': bool
        },


    }

    modified_settings = settings._mod_settings # check only modified settings

    # check settings keys:
    for setting in modified_settings:
        if setting not in settings_values:
            raise SettingValidationError('"{}" is not a valid setting'.format(setting))

    for setting_name, setting_value in modified_settings.items():
        setting_type = type(setting_value)
        setting_props = settings_values[setting_name]

        # check type:
        if not setting_type == setting_props['type']:
            raise SettingValidationError(
                "'{}' must be '{}', not '{}'.".format(
                    setting_name, setting_props['type'].__name__, setting_type.__name__
                )
            )

        # check values:
        if setting_props['values'] and setting_value not in setting_props['values']:
            raise SettingValidationError(
                "\"{}\" is not a valid value for {}, it should be: '{}' or '{}'.".format(
                    setting_value,
                    setting_name,
                    "', '".join(setting_props['values'][:-1]),
                    setting_props['values'][-1],
                )
            )
