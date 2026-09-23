__version__ = "1.4.3"

import collections
from collections.abc import Callable, Iterable, Iterator
from datetime import datetime
from typing import Any

from .conf import apply_settings
from .date import DateDataParser
from .parser import date_order_chart

_default_parser = DateDataParser()


@apply_settings
def parse(
    date_string,
    date_formats=None,
    languages=None,
    locales=None,
    region=None,
    settings=None,
    detect_languages_function=None,
):
    """Parse date and time from given date string.

    :param date_string:
        A string representing date and/or time in a recognizably valid format.
    :type date_string: str

    :param date_formats:
        A list of format strings using directives as given
        `here <https://docs.python.org/2/library/datetime.html#strftime-and-strptime-behavior>`_.
        The parser applies formats one by one, taking into account the detected languages/locales.
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

    if data:
        return data["date_obj"]


class AmbiguousDateOrderError(ValueError):
    """Raised by :func:`parse_many` when more than one date order fits the date
    strings. *date_strings* holds the pending date strings, which
    :func:`parse_many` has not yielded, and *date_orders* the date orders that
    fit them."""

    def __init__(self, date_strings: list[str], date_orders: list[str]):
        super().__init__(
            f"Ambiguous date order, could be any of: {', '.join(date_orders)}"
        )
        self.date_strings = date_strings
        self.date_orders = date_orders


def parse_many(
    date_strings: Iterable[str],
    languages: list[str] | None = None,
    locales: list[str] | None = None,
    region: str | None = None,
    settings: dict[str, Any] | None = None,
    detect_languages_function: Callable[[str, float], list[str]] | None = None,
    max_pending: int | None = None,
) -> Iterator[datetime | None]:
    """Parse *date_strings* with the date order that fits all of them.

    Returns an iterator of :class:`~datetime.datetime` objects. For example, in
    ``['2015/2/3', '2015/31/12']``, the second date string shows that the first
    one is 2 March 2015, while :func:`parse` would read it as 3 February 2015.
    Date strings that cannot be parsed become ``None``, and do not count when
    finding the date order.

    Date strings that different date orders parse differently stay pending
    until a later date string settles the date order, so input that settles it
    late keeps many date strings in memory. Shuffling the input, where
    feasible, helps. If more than *max_pending* date strings are pending, or
    the input ends while some are, :exc:`AmbiguousDateOrderError` is raised,
    unless the ``DATE_ORDER`` setting is one of the date orders that fit, in
    which case it is used.

    Raises :exc:`ValueError` if a date string does not fit any date order that
    fits the previous ones.
    """
    settings = dict(settings or {})
    preferred_order = settings.get("DATE_ORDER")
    # Relative dates must not change from one date order to the next.
    settings.setdefault("RELATIVE_BASE", datetime.now())
    parser_kwargs = {
        "languages": languages,
        "locales": locales,
        "region": region,
        "detect_languages_function": detect_languages_function,
    }
    parser = DateDataParser(settings=settings, **parser_kwargs)
    strict_parsers = {}

    def parse_strictly(date_string, order, locale):
        # Parsing with the locale of regular parsing, because a date string
        # that fails under one locale is tried under every other one.
        if (order, locale) not in strict_parsers:
            strict_parsers[order, locale] = DateDataParser(
                locales=[locale],
                settings={**settings, "DATE_ORDER": order, "STRICT_DATE_ORDER": True},
            )
        return strict_parsers[order, locale].get_date_data(date_string)["date_obj"]

    orders = list(date_order_chart)
    pending: collections.deque[tuple[str, dict[str, datetime | None]]] = (
        collections.deque()
    )
    locked_parser = None
    for date_string in date_strings:
        if locked_parser:
            date = locked_parser.get_date_data(date_string)["date_obj"]
            if date is None and parser.get_date_data(date_string)["date_obj"]:
                raise ValueError(
                    f"{date_string!r} does not fit the {orders[0]} date order"
                )
            yield date
            continue
        locale = parser.get_date_data(date_string)["locale"]
        if locale is None:
            dates = dict.fromkeys(orders)
        else:
            dates = {
                order: parse_strictly(date_string, order, locale) for order in orders
            }
            orders = [order for order in orders if dates[order]]
            if not orders:
                raise ValueError(
                    f"No date order fits {date_string!r} and the previous date strings"
                )
        pending.append((date_string, dates))
        while pending and len({pending[0][1][order] for order in orders}) == 1:
            yield pending.popleft()[1][orders[0]]
        if max_pending is not None and len(pending) > max_pending:
            orders = _settle_date_order(pending, orders, preferred_order)
            while pending:
                yield pending.popleft()[1][orders[0]]
        if len(orders) == 1:
            locked_parser = DateDataParser(
                settings={
                    **settings,
                    "DATE_ORDER": orders[0],
                    "STRICT_DATE_ORDER": True,
                },
                **parser_kwargs,
            )
    if pending:
        order = _settle_date_order(pending, orders, preferred_order)[0]
        for _, dates in pending:
            yield dates[order]


def _settle_date_order(pending, orders, preferred_order):
    if preferred_order in orders:
        return [preferred_order]
    raise AmbiguousDateOrderError([date_string for date_string, _ in pending], orders)
