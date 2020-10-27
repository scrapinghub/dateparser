import hashlib
from functools import wraps

from .utils import registry


@registry
class Settings:
    """Control and configure default parsing behavior of dateparser.
    Currently, supported settings are:

    * `DATE_ORDER`
    * `PREFER_LOCALE_DATE_ORDER`
    * `TIMEZONE`
    * `TO_TIMEZONE`
    * `RETURN_AS_TIMEZONE_AWARE`
    * `PREFER_DAY_OF_MONTH`
    * `PREFER_DATES_FROM`
    * `RELATIVE_BASE`
    * `STRICT_PARSING`
    * `REQUIRE_PARTS`
    * `SKIP_TOKENS`
    * `NORMALIZE`
    * `RETURN_TIME_AS_PERIOD`
    * `PARSERS`
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
        for k, v in kwds.items():
            if v is None:
                raise TypeError('Invalid {{"{}": {}}}'.format(k, v))

        for x in self._get_settings_from_pyfile().keys():
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
            kwargs['settings'] = settings.replace(mod_settings=mod_settings, **kwargs['settings'])

        if not isinstance(kwargs['settings'], Settings):
            raise TypeError(
                "settings can only be either dict or instance of Settings class")

        return f(*args, **kwargs)
    return wrapper
