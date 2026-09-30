from dataclasses import dataclass, fields
from datetime import time
from enum import Enum

import regex as re


class PartOfDay(str, Enum):
    """Part of the day that a date string refers to, e.g. ``"tonight"``.

    See :attr:`DateData.part_of_day <dateparser.date.DateData.part_of_day>`.

    .. versionadded:: VERSION
    """

    EARLY_MORNING = "early_morning"
    """Between midnight and dawn, e.g. ``"in the small hours"`` or Spanish
    ``"de madrugada"``."""

    MORNING = "morning"
    AFTERNOON = "afternoon"
    EVENING = "evening"
    NIGHT = "night"


@dataclass(frozen=True)
class PartsOfDay:
    """Time of the day to use for each :class:`PartOfDay`, for the
    ``PARTS_OF_DAY`` :ref:`setting <settings>`.

    .. versionadded:: VERSION
    """

    early_morning: time = time(3)
    morning: time = time(9)
    afternoon: time = time(15)
    evening: time = time(18)
    night: time = time(20)

    def __post_init__(self) -> None:
        for field in fields(self):
            value = getattr(self, field.name)
            if not isinstance(value, time):
                raise TypeError(
                    f"{type(self).__name__}.{field.name} must be a datetime.time, "
                    f"not {type(value).__name__}"
                )


_PART_OF_DAY_PATTERN = re.compile(
    r"(?<!\S)(" + "|".join(part.value for part in PartOfDay) + r")(?!\S)"
)
_TIME_PATTERN = re.compile(r"\d\s*(?::|(?:am|pm)(?!\S))")
_MONTHS = (
    "january|february|march|april|may|june|july|august|september|october|"
    "november|december"
)
_TRAILING_NUMBER_PATTERN = re.compile(
    rf"(?<![\d:/.-])(?P<month>(?<!\d\s*)(?:{_MONTHS})\s+)?"
    r"(?P<hour>\d{1,2})(?P<minutes>:\d{2})?\s*$"
)


def _meridiem(part: PartOfDay, hour: int) -> str:
    if part in (PartOfDay.EARLY_MORNING, PartOfDay.MORNING):
        return "am"
    if part is PartOfDay.NIGHT and not 6 <= hour <= 11:
        return "am"
    return "pm"


def _replace_part_of_day(
    translated: str, parts_of_day: PartsOfDay
) -> tuple[str, PartOfDay | None, bool]:
    """Return *translated* with its part-of-day token replaced by a time, the
    matching :class:`PartOfDay` (or ``None``), and whether that time came from
    *parts_of_day*.

    A number right before the part of the day is an hour, e.g. ``"8 in the
    evening"``, unless a month without a day precedes it, e.g. ``"January 8 in
    the evening"``. A part of the day on its own is left in place, so that
    parsing fails."""
    match = _PART_OF_DAY_PATTERN.search(translated)
    if not match:
        return translated, None, False
    part = PartOfDay(match[1])
    before, after = translated[: match.start()], translated[match.end() :]
    number = _TRAILING_NUMBER_PATTERN.search(before)
    if number and not number["month"]:
        hour = int(number["hour"])
        if hour > 12:
            return translated, None, False
        time_string = f"{hour}{number['minutes'] or ':00'} {_meridiem(part, hour)}"
        return f"{before[: number.start()]}{time_string} {after}", part, False
    rest = f"{before} {after}"
    if not rest.strip():
        return translated, None, False
    if _TIME_PATTERN.search(rest):
        return rest, part, False
    part_time: time = getattr(parts_of_day, part.value)
    return f"{rest} {part_time:%H:%M:%S}", part, True
