import hashlib
from collections.abc import Callable, Iterable, Mapping
from datetime import datetime
from functools import wraps
from types import MappingProxyType
from typing import Any, Literal, ParamSpec, TypeVar

from dateparser._parts_of_day import PartsOfDay
from dateparser.data.languages_info import language_order

from .parser import date_order_chart
from .utils import registry

_P = ParamSpec("_P")
_R = TypeVar("_R")


@registry
class Settings:
    """Control and configure default parsing behavior of dateparser.
    Currently, supported settings are:

    * `DATE_ORDER`
    * `PREFER_LOCALE_DATE_ORDER`
    * `STRICT_DATE_ORDER`
    * `TIMEZONE`
    * `TO_TIMEZONE`
    * `RETURN_AS_TIMEZONE_AWARE`
    * `PREFER_MONTH_OF_YEAR`
    * `PREFER_DAY_OF_MONTH`
    * `PREFER_DATES_FROM`
    * `RELATIVE_BASE`
    * `STRICT_PARSING`
    * `REQUIRE_PARTS`
    * `IGNORE_SURROUNDING_TEXT`
    * `SKIP_TOKENS`
    * `NORMALIZE`
    * `RETURN_TIME_AS_PERIOD`
    * `RETURN_TIME_SPAN`
    * `DEFAULT_START_OF_WEEK`
    * `DEFAULT_DAYS_IN_MONTH`
    * `PARTS_OF_DAY`
    * `PARSERS`
    * `DEFAULT_LANGUAGES`
    * `USE_GIVEN_LANGUAGE_ORDER`
    * `LANGUAGE_DETECTION_CONFIDENCE_THRESHOLD`
    * `CACHE_SIZE_LIMIT`
    """

    _default: bool = True
    _pyfile_data: dict[str, Any] | None = None
    _mod_settings: Mapping[str, Any] = MappingProxyType({})

    registry_key: str
    DATE_ORDER: str
    PREFER_LOCALE_DATE_ORDER: bool
    STRICT_DATE_ORDER: str
    TIMEZONE: str
    TO_TIMEZONE: str | Literal[False]
    RETURN_AS_TIMEZONE_AWARE: bool | Literal["default"]
    PREFER_MONTH_OF_YEAR: str
    PREFER_DAY_OF_MONTH: str
    PREFER_DATES_FROM: str
    RELATIVE_BASE: datetime | Literal[False]
    STRICT_PARSING: bool
    REQUIRE_PARTS: list[str]
    IGNORE_SURROUNDING_TEXT: bool
    SKIP_TOKENS: list[str]
    NORMALIZE: bool
    RETURN_TIME_AS_PERIOD: bool
    RETURN_TIME_SPAN: bool
    DEFAULT_START_OF_WEEK: str
    DEFAULT_DAYS_IN_MONTH: int
    PARTS_OF_DAY: PartsOfDay
    PARSERS: list[str]
    DEFAULT_LANGUAGES: list[str]
    USE_GIVEN_LANGUAGE_ORDER: bool
    LANGUAGE_DETECTION_CONFIDENCE_THRESHOLD: float
    CACHE_SIZE_LIMIT: int

    def __init__(self, settings: Mapping[str, Any] | None = None) -> None:
        if settings:
            self._updateall(settings.items())
        else:
            self._updateall(self._get_settings_from_pyfile().items())

    @classmethod
    def get_key(cls, settings: Mapping[str, Any] | None = None) -> str:
        if not settings:
            return "default"

        keys = sorted([f"{key}-{settings[key]}" for key in settings])
        return hashlib.md5(
            "".join(keys).encode("utf-8"), usedforsecurity=False
        ).hexdigest()

    @classmethod
    def _get_settings_from_pyfile(cls) -> dict[str, Any]:
        if not cls._pyfile_data:
            from dateparser_data import settings  # noqa: PLC0415

            cls._pyfile_data = settings.settings
        return cls._pyfile_data

    def _updateall(self, iterable: Iterable[tuple[str, Any]]) -> None:
        for key, value in iterable:
            setattr(self, key, value)

    def replace(
        self, mod_settings: Mapping[str, Any] | None = None, **kwds: Any
    ) -> "Settings":
        for k, v in kwds.items():
            if v is None:
                raise TypeError(f'Invalid {{"{k}": {v}}}')

        for x in self._get_settings_from_pyfile():
            kwds.setdefault(x, getattr(self, x))

        kwds["_default"] = False
        # Keep track of the settings that the caller set, or replacing another
        # one, like RELATIVE_BASE, makes an explicit DATE_ORDER give way to the
        # order of the locale.
        if mod_settings is None:
            mod_settings = self._mod_settings
        if mod_settings:
            kwds["_mod_settings"] = mod_settings

        return self.__class__(settings=kwds)


settings = Settings()


def apply_settings(f: Callable[_P, _R]) -> Callable[_P, _R]:
    @wraps(f)
    def wrapper(*args: _P.args, **kwargs: _P.kwargs) -> _R:
        mod_settings: Any = kwargs.get("settings")
        kwargs["settings"] = mod_settings or settings

        if isinstance(kwargs["settings"], dict):
            kwargs["settings"] = settings.replace(
                mod_settings=mod_settings, **kwargs["settings"]
            )

        if not isinstance(kwargs["settings"], Settings):
            raise TypeError(
                "settings can only be either dict or instance of Settings class"
            )

        return f(*args, **kwargs)

    return wrapper


class SettingValidationError(ValueError):
    pass


def _check_repeated_values(setting_name: str, setting_value: list[Any]) -> None:
    if len(setting_value) != len(set(setting_value)):
        raise SettingValidationError(
            f'There are repeated values in the "{setting_name}" setting'
        )


def _check_require_part(setting_name: str, setting_value: list[str]) -> None:
    """Returns `True` if the provided list of parts contains valid values"""
    invalid_values = set(setting_value) - {"day", "month", "year"}
    if invalid_values:
        raise SettingValidationError(
            '"{}" setting contains invalid values: {}'.format(
                setting_name, ", ".join(invalid_values)
            )
        )
    _check_repeated_values(setting_name, setting_value)


def _check_parsers(setting_name: str, setting_value: list[str]) -> None:
    """Returns `True` if the provided list of parsers contains valid values"""
    from dateparser.date import _DateLocaleParser  # noqa: PLC0415

    unknown_parsers = set(setting_value) - _DateLocaleParser._parsers.keys()
    if unknown_parsers:
        raise SettingValidationError(
            'Found unknown parsers in the "{}" setting: {}'.format(
                setting_name, ", ".join(unknown_parsers)
            )
        )
    _check_repeated_values(setting_name, setting_value)


def _check_default_languages(setting_name: str, setting_value: list[str]) -> None:
    unsupported_languages = set(setting_value) - set(language_order)
    if unsupported_languages:
        raise SettingValidationError(
            "Found invalid languages in the '{}' setting: {}".format(
                setting_name, ", ".join(map(repr, unsupported_languages))
            )
        )
    _check_repeated_values(setting_name, setting_value)


def _check_between_0_and_1(setting_name: str, setting_value: float) -> None:
    is_valid = 0 <= setting_value <= 1
    if not is_valid:
        raise SettingValidationError(
            f"{setting_value} is not a valid value for {setting_name}. It can take "
            "values between 0 and 1."
        )


def check_settings(settings: Settings) -> None:
    """
    Check if provided settings are valid, if not it raises `SettingValidationError`.
    Only checks for the modified settings.
    """
    settings_values: dict[str, dict[str, Any]] = {
        "DATE_ORDER": {
            "values": tuple(date_order_chart.keys()),
            "type": str,
        },
        "TIMEZONE": {
            # we don't check invalid Timezones as they raise an error
            "type": str,
        },
        "TO_TIMEZONE": {
            # It defaults to None, but it's not allowed to use it directly
            # "values" can take unlimited options
            "type": str
        },
        "RETURN_AS_TIMEZONE_AWARE": {
            # It defaults to 'default', but it's not allowed to use it directly
            "type": bool
        },
        "PREFER_MONTH_OF_YEAR": {"values": ("current", "first", "last"), "type": str},
        "PREFER_DAY_OF_MONTH": {"values": ("current", "first", "last"), "type": str},
        "PREFER_DATES_FROM": {
            "values": ("current_period", "past", "future"),
            "type": str,
        },
        "RELATIVE_BASE": {
            # "values" can take unlimited options
            "type": datetime
        },
        "STRICT_PARSING": {"type": bool},
        "IGNORE_SURROUNDING_TEXT": {"type": bool},
        "REQUIRE_PARTS": {
            # "values" covered by the 'extra_check'
            "type": list,
            "extra_check": _check_require_part,
        },
        "SKIP_TOKENS": {
            # "values" can take unlimited options
            "type": list,
        },
        "NORMALIZE": {"type": bool},
        "RETURN_TIME_AS_PERIOD": {"type": bool},
        "PARSERS": {
            # "values" covered by the 'extra_check'
            "type": list,
            "extra_check": _check_parsers,
        },
        "FUZZY": {"type": bool},
        "PREFER_LOCALE_DATE_ORDER": {"type": bool},
        "STRICT_DATE_ORDER": {"values": ("none", "year", "all"), "type": str},
        "DEFAULT_LANGUAGES": {"type": list, "extra_check": _check_default_languages},
        "USE_GIVEN_LANGUAGE_ORDER": {"type": bool},
        "LANGUAGE_DETECTION_CONFIDENCE_THRESHOLD": {
            "type": float,
            "extra_check": _check_between_0_and_1,
        },
        "CACHE_SIZE_LIMIT": {
            "type": int,
        },
        "RETURN_TIME_SPAN": {"type": bool},
        "DEFAULT_START_OF_WEEK": {
            "values": ("monday", "sunday"),
            "type": str,
        },
        "DEFAULT_DAYS_IN_MONTH": {
            "type": int,
        },
        "PARTS_OF_DAY": {"type": PartsOfDay},
    }

    modified_settings = settings._mod_settings  # check only modified settings

    # check settings keys:
    for setting in modified_settings:
        if setting not in settings_values:
            raise SettingValidationError(f'"{setting}" is not a valid setting')

    for setting_name, setting_value in modified_settings.items():
        setting_type = type(setting_value)
        setting_props = settings_values[setting_name]

        # check type:
        if not isinstance(setting_value, setting_props["type"]):
            raise SettingValidationError(
                '"{}" must be "{}", not "{}".'.format(
                    setting_name, setting_props["type"].__name__, setting_type.__name__
                )
            )

        # check values:
        if setting_props.get("values") and setting_value not in setting_props["values"]:
            raise SettingValidationError(
                '"{}" is not a valid value for "{}", it should be: "{}" or "{}"'.format(
                    setting_value,
                    setting_name,
                    '", "'.join(setting_props["values"][:-1]),
                    setting_props["values"][-1],
                )
            )

        # specific checks
        extra_check = setting_props.get("extra_check")
        if extra_check:
            extra_check(setting_name, setting_value)

    # STRICT_DATE_ORDER enforces the DATE_ORDER that the caller sets. The default
    # one is only a preference, so without it there is nothing to enforce.
    strict_date_order = modified_settings.get("STRICT_DATE_ORDER", "none")
    if strict_date_order != "none" and "DATE_ORDER" not in modified_settings:
        raise SettingValidationError(
            f'"STRICT_DATE_ORDER": "{strict_date_order}" requires the "DATE_ORDER" '
            "setting"
        )
