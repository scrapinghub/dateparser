import re
from datetime import timedelta

from dateutil.relativedelta import relativedelta


def detect_time_span(text):
    """Detect time span expressions in text and return span information."""
    span_patterns = [
        {
            "pattern": r"\b(?:for\s+the\s+|during\s+the\s+|in\s+the\s+)?(?:past|last|previous)\s+month\b",
            "type": "month",
            "direction": "past",
        },
        {
            "pattern": r"\b(?:for\s+the\s+|during\s+the\s+|in\s+the\s+)?(?:past|last|previous)\s+week\b",
            "type": "week",
            "direction": "past",
        },
        {
            "pattern": r"\b(?:for\s+the\s+|during\s+the\s+|in\s+the\s+)?(?:past|last|previous)\s+(\d+)\s+days?\b",
            "type": "days",
            "direction": "past",
        },
        {
            "pattern": r"\b(?:for\s+the\s+|during\s+the\s+|in\s+the\s+)?(?:past|last|previous)\s+(\d+)\s+weeks?\b",
            "type": "weeks",
            "direction": "past",
        },
        {
            "pattern": r"\b(?:for\s+the\s+|during\s+the\s+|in\s+the\s+)?(?:past|last|previous)\s+(\d+)\s+months?\b",
            "type": "months",
            "direction": "past",
        },
        {
            "pattern": r"\b(?:for\s+the\s+|during\s+the\s+|in\s+the\s+)?(?:next|coming|following)\s+month\b",
            "type": "month",
            "direction": "future",
        },
        {
            "pattern": r"\b(?:for\s+the\s+|during\s+the\s+|in\s+the\s+)?(?:next|coming|following)\s+week\b",
            "type": "week",
            "direction": "future",
        },
        {
            "pattern": r"\b(?:for\s+the\s+|during\s+the\s+|in\s+the\s+)?(?:next|coming|following)\s+(\d+)\s+days?\b",
            "type": "days",
            "direction": "future",
        },
        {
            "pattern": r"\b(?:for\s+the\s+|during\s+the\s+|in\s+the\s+)?(?:next|coming|following)\s+(\d+)\s+weeks?\b",
            "type": "weeks",
            "direction": "future",
        },
        {
            "pattern": r"\b(?:for\s+the\s+|during\s+the\s+|in\s+the\s+)?(?:next|coming|following)\s+(\d+)\s+months?\b",
            "type": "months",
            "direction": "future",
        },
    ]

    for pattern_info in span_patterns:
        match = re.search(pattern_info["pattern"], text, re.IGNORECASE)
        if match:
            result = {
                "type": pattern_info["type"],
                "direction": pattern_info["direction"],
                "matched_text": match.group(0),
                "start_pos": match.start(),
                "end_pos": match.end(),
            }

            if match.groups():
                result["number"] = int(match.group(1))

            return result

    return None


def generate_time_span(span_info, base_date, settings):
    """Return the start and end dates of the span described by *span_info*."""
    span_type = span_info["type"]
    number = span_info.get("number", 1)
    past = span_info["direction"] == "past"

    if span_type == "week":
        days_back = base_date.weekday()
        if settings.DEFAULT_START_OF_WEEK == "sunday":
            days_back = (days_back + 1) % 7
        week_start = base_date - timedelta(days=days_back)
        if past:
            return week_start - timedelta(days=7), week_start - timedelta(days=1)
        start_date = week_start + timedelta(days=7)
        return start_date, start_date + timedelta(days=6)

    if span_type == "month":
        span = timedelta(days=settings.DEFAULT_DAYS_IN_MONTH)
    elif span_type == "days":
        span = timedelta(days=number)
    elif span_type == "weeks":
        span = timedelta(weeks=number)
    else:
        span = relativedelta(months=number)

    if past:
        return base_date - span, base_date
    return base_date, base_date + span
