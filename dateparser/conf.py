# -*- coding: utf-8 -*-

class Settings(object):
    PREFER_DATES_FROM_FUTURE = None
    SUPPORT_BEFORE_COMMON_ERA = False

    def __init__(self, **kwargs):
        for key in kwargs:
            setattr(self, key, kwargs[key])

    def update(self, key, value):
        setattr(self, key, value)

def reload_settings():
    global settings
    settings = Settings()

settings = Settings()