__version__ = "1.5.1"

from collections import deque
from collections.abc import Callable, Iterable, Iterator
from datetime import datetime
from typing import Any

from ._parts_of_day import PartOfDay as PartOfDay
from ._parts_of_day import PartsOfDay as PartsOfDay
from .conf import Settings, apply_settings
from .date import DateDataParser as DateDataParser
from .parser import date_order_chart
from .utils import _now

_default_parser = DateDataParser()


@apply_settings
def parse(
    date_string: str,
    date_formats: Iterable[str] | None = None,
    languages: Iterable[str] | None = None,
    locales: Iterable[str] | None = None,
    region: str | None = None,
    settings: Settings | dict[str, Any] | None = None,
    detect_languages_function: Callable[..., list[str]] | None = None,
) -> datetime | None:
    """Parse date and time from given date string.

    :param date_string:
        A string representing date and/or time in a recognizably valid format.
    :type date_string: str

    :param date_formats:
        A list of format strings using directives as given
        `here <https://docs.python.org/2/library/datetime.html#strftime-and-strptime-behavior>`_.
        The parser applies formats one by one, taking into account the detected
        languages/locales. A UTC offset matched by ``%z`` is kept, while a time
        zone name matched by ``%Z`` is ignored. If no format matches, the other
        parsers of the :ref:`PARSERS <settings>` setting are tried; set it to
        ``['custom-formats']`` to use only these formats.
    :type date_formats: list

    :param languages:
        A list of language codes, e.g. ['en', 'es', 'zh-Hant'].
        If locales are not given, languages and region are used to construct locales for translation.
    :type languages: list

    :param locales:
        A list of locale codes, e.g. ['fr-PF', 'qu-EC', 'af-NA'].
        The parser uses only these locales to translate date string.
    :type locales: list

    :param region:
        A region code, e.g. 'IN', '001', 'NE'.
        If locales are not given, languages and region are used to construct locales for translation.
    :type region: str

    :param settings:
        Configure customized behavior using settings defined in :mod:`dateparser.conf.Settings`.
    :type settings: dict

    :param detect_languages_function:
        A function for language detection that takes as input a string (the `date_string`) and
        a `confidence_threshold`, and returns a list of detected language codes.
        Note: this function is only used if ``languages`` and ``locales`` are not provided.
    :type detect_languages_function: function

    :return: Returns :class:`datetime <datetime.datetime>` representing parsed date if successful, else returns None
    :rtype: :class:`datetime <datetime.datetime>`.
    :raises:
        ``ValueError``: Unknown Language, ``TypeError``: Languages argument must be a list,
        ``SettingValidationError``: A provided setting is not valid.
    """
    assert isinstance(settings, Settings)
    parser = _default_parser

    if (
        languages
        or locales
        or region
        or detect_languages_function
        or not settings._default
    ):
        parser = DateDataParser(
            languages=languages,
            locales=locales,
            region=region,
            settings=settings,
            detect_languages_function=detect_languages_function,
        )

    data = parser.get_date_data(date_string, date_formats)
    date_obj: datetime | None = data["date_obj"]
    return date_obj


def parse_many(
    date_strings: Iterable[str],
    languages: list[str] | None = None,
    locales: list[str] | None = None,
    region: str | None = None,
    settings: dict[str, Any] | None = None,
    detect_languages_function: Callable[[str, float], list[str]] | None = None,
    max_pending: int | None = None,
    date_orders: Iterable[str] | None = None,
) -> Iterator[datetime | None]:
    """Parse *date_strings* with the date order that fits all of them.

    Returns an iterator of :class:`~datetime.datetime` objects. For example, in
    ``['2015/2/3', '2015/31/12']``, the second date string shows that the first
    one is 2 March 2015, while :func:`parse` would read it as 3 February 2015.
    Date strings that cannot be parsed become ``None``. Date strings that fit
    none of the date orders that fit the previous ones are parsed with the
    ``DATE_ORDER`` setting set to the date order of the others, so the
    ``STRICT_DATE_ORDER`` setting decides whether they become ``None``. Neither
    counts when finding the date order.

    *date_orders* limits the candidate date orders, e.g. to ``["DMY", "MDY"]``
    to only tell days and months apart. By default, all date orders are
    candidates.

    Date strings that different date orders parse differently stay pending
    until a later date string settles the date order, so input that settles it
    late keeps many date strings in memory. Shuffling the input, where
    feasible, helps. Date strings still pending when the input ends, or once
    more than *max_pending* are pending, are parsed as :func:`parse` would.
    """
    orders = list(date_order_chart if date_orders is None else date_orders)
    if not orders or not set(orders) <= set(date_order_chart):
        raise ValueError(f"Invalid date_orders: {date_orders!r}")
    parser_kwargs: dict[str, Any] = {
        "languages": languages,
        "locales": locales,
        "region": region,
        "detect_languages_function": detect_languages_function,
    }
    settings = settings or {}
    parser = DateDataParser(settings=settings, **parser_kwargs)
    # Relative dates must not change from one date order to the next while
    # finding the date order.
    strict_settings = {"RELATIVE_BASE": _now(parser._settings), **settings}
    strict_parsers: dict[tuple[str, str], DateDataParser] = {}
    order_parsers: dict[str, DateDataParser] = {}

    def parse_strictly(date_string: str, order: str, locale: str) -> datetime | None:
        # Parsing with the locale of regular parsing, because a date string
        # that fails under one locale is tried under every other one.
        if (order, locale) not in strict_parsers:
            strict_parsers[order, locale] = DateDataParser(
                locales=[locale],
                settings={
                    **strict_settings,
                    "DATE_ORDER": order,
                    "STRICT_DATE_ORDER": "all",
                },
            )
        date_obj: datetime | None = strict_parsers[order, locale].get_date_data(
            date_string
        )["date_obj"]
        return date_obj

    def parse_in_order(date_string: str, order: str) -> datetime | None:
        if order not in order_parsers:
            order_parsers[order] = DateDataParser(
                settings={**settings, "DATE_ORDER": order}, **parser_kwargs
            )
        date_obj: datetime | None = order_parsers[order].get_date_data(date_string)[
            "date_obj"
        ]
        return date_obj

    def pop(order: str | None) -> datetime | None:
        date_string = pending.popleft()[0]
        if date_string is None:
            return None
        if order is None:
            date_obj: datetime | None = parser.get_date_data(date_string)["date_obj"]
            return date_obj
        return parse_in_order(date_string, order)

    # Pending date strings, or None for those that cannot be parsed, with what
    # they become in each date order.
    pending: deque[tuple[str | None, dict[str, datetime | None]]] = deque()
    for date_string in date_strings:
        if len(orders) == 1:
            yield parse_in_order(date_string, orders[0])
            continue
        data = parser.get_date_data(date_string)
        if data["locale"] is None:
            pending.append((None, dict.fromkeys(orders)))
        else:
            dates = {
                order: parse_strictly(date_string, order, data["locale"])
                for order in orders
            }
            if any(dates.values()):
                orders = [order for order in orders if dates[order]]
            else:
                dates = {order: parse_in_order(date_string, order) for order in orders}
            pending.append((date_string, dates))
        while pending and len({pending[0][1][order] for order in orders}) == 1:
            yield pop(orders[0])
        if max_pending is not None and len(pending) > max_pending:
            yield pop(None)
    while pending:
        yield pop(None)
