# -*- coding: utf-8 -*-
from pkgutil import get_data

from itertools import chain
from functools import wraps
from yaml import load as load_yaml

from .utils import Registry


class SettingsRegistry(Registry):

    @classmethod
    def get_key(cls, *args, **kwargs):
        if not args and not kwargs:
            return 'default'

        keys= sorted(['%s-%s' % (key, str(kwargs[key])) for key in kwargs])
        return ''.join(keys)


class Settings(object):

    __metaclass__ = SettingsRegistry

    _attributes = []
    _default = True

    def __init__(self, **kwargs):
        """
        Settings are now loaded using the data/settings.yaml file.
        """
        self._updateall(
            chain(self._get_settings_from_yaml().items(),
            kwargs.items())
        )

    def _get_settings_from_yaml(self):
        data = get_data('data', 'settings.yaml')
        data = load_yaml(data)
        return data.pop('settings', {})

    def _updateall(self, iterable):
        for key, value in iterable:
            self._attributes.append(key)
            setattr(self, key, value)

    def replace(self, **kwds):
        for x in self._attributes:
            kwds.setdefault(x, getattr(self, x))
        kwds['_default'] = False

        return self.__class__(**kwds)


settings = Settings()


def apply_settings(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'settings' in kwargs:
            if isinstance(kwargs['settings'], dict):
                kwargs['settings'] = settings.replace(**kwargs['settings'])
            elif isinstance(kwargs['settings'], Settings):
                kwargs['settings'] = kwargs['settings']
            else:
                raise TypeError("settings can only be either dict or instance of Settings class")
        else:
            kwargs['settings'] = settings
        return f(*args, **kwargs)
    return wrapper
