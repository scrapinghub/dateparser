default_parsers = [
    'timestamp',
    'relative-time',
    'custom-formats',
    'absolute-time',
]

settings = {
    'PREFER_DATES_FROM': 'current_period',
    'PREFER_DAY_OF_MONTH': 'current',
    'SKIP_TOKENS': ["t"],
    'TIMEZONE': 'local',
    'TO_TIMEZONE': False,
    'RETURN_AS_TIMEZONE_AWARE': 'default',
    'NORMALIZE': True,
    'RELATIVE_BASE': False,
    'DATE_ORDER': 'MDY',
    'PREFER_LOCALE_DATE_ORDER': True,
    'FUZZY': False,
    'STRICT_PARSING': False,
    'RETURN_TIME_AS_PERIOD': False,
    'PARSERS': default_parsers,
    'REQUIRE_PARTS': [],
}
