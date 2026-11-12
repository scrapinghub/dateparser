"""The standard library's warning about a day of month without a year."""

# The part of the message that is the same in every spelling of it (Python 3.13
# writes "ambiguious", Python 3.14 "ambiguous"). The guards that parsing a date
# without a year does not make the standard library warn look for it.
DAY_WITHOUT_YEAR_WARNING = "day of month without a year specified"
