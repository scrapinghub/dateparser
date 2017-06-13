# coding: utf-8
from dateparser.languages.loader import LanguageDataLoader
from dateparser.conf import Settings


class ExactLanguageSearch:
    def __init__(self):
        self.loader = LanguageDataLoader()
        self.language = None

    def get_current_language(self, shortname):
        if self.language is None or self.language.shortname != shortname:
            self.language = self.loader.get_language(shortname)

    def search(self, shortname, text):
        self.get_current_language(shortname)
        translated, original = self.language.translate_search(text, settings=Settings())
        return translated, original

el = ExactLanguageSearch()
# print(el.search('ru', '5 января 2005 все отдыхали, 6 января все отдыхали, '
#                 '7 января все отдыхали, в понедельник пришлось выйти на работу'))
print(el.search('en', 'Game 1 is July 12, 2017. Game 2 on July 13th. Game 3 on July 15th'))
print(el.search('en', 'I will meet you tomorrow at noon'))
print(el.search('ru', 'July 3, 2017 - August 1st'))
print(el.search('en', 'in a minute'))
print(el.search('en', 'July 13th, July 14th'))
print(el.search('en', 'July 13th. July 14th'))
