import dateparser

# date_obj = dateparser.parse('Feb 2009')

# date_obj = dateparser.parse('1y')
# date_obj = dateparser.parse('1y ago')
# date_obj = dateparser.parse('"22Mei2010 02h04"', date_formats=['%d%B%Y %Hh%M'])
# date_obj = dateparser.parse('1y', languages=['en'])

# date_obj = dateparser.parse('07/03/2009')
# date_obj = dateparser.parse("Do I have anything on the next month?")
# date_obj = dateparser.parse('20171222160001')

# date_obj = dateparser.parse('10 days ago')
# date_obj = dateparser.parse('in 2 days')
# date_obj = dateparser.parse('en 2 días')
# date_obj = dateparser.parse('2009')
# date_obj = dateparser.parse('07/03/2009', locales=['fr'])


# date_obj = dateparser.parse('a')
# date_obj = dateparser.parse('20110101')
date_obj = dateparser.parse('02/2013', ['%m/%Y'])
print(date_obj)

# from dateparser import search as se
# print(se.search_dates("Do I have anything on the next month?", settings={"PREFER_DATES_FROM" : "future"}, languages=['es']))
