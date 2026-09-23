from dateparser.calendars import non_gregorian_parser


def test_to_latin_defaults():
    assert non_gregorian_parser.to_latin(" 1 x ") == "1 x"
