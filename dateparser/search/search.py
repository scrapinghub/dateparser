# coding: utf-8
from dateparser.languages.loader import LanguageDataLoader
from dateparser.conf import Settings
from dateparser.date import DateDataParser
import datetime


class ExactLanguageSearch:
    def __init__(self):
        self.loader = LanguageDataLoader()
        self.language = None

    def get_current_language(self, shortname):
        if self.language is None or self.language.shortname != shortname:
            self.language = self.loader.get_language(shortname)

    def search(self, shortname, text):
        self.get_current_language(shortname)
        result = self.language.translate_search(text, settings=Settings())
        return result

    @staticmethod
    def set_relative_base(pre_parsed_object, substring, already_parsed, is_relative,  settings):
        if settings:
            if "RELATIVE_BASE" in settings:
                return substring, None
        elif pre_parsed_object['period'] == 'year' and not is_relative:
            return substring, datetime.datetime(2000, 1, 1, 0)
        elif len(already_parsed) == 0:
            return substring, None
        else:
            i = len(already_parsed) - 1
            while already_parsed[i]['is_relative']:
                i -= 1
                if i == -1:
                    return substring, None
            relative_base = already_parsed[i]['date_obj']
            return substring, relative_base

    @staticmethod
    def date_is_relative(translation):
        if "ago" in translation or "in" in translation or "from now" in translation or "tomorrow" in translation \
                or "today" in translation or "yesterday" in translation:

            return True
        else:
            return False

    def choose_best_split(self, possible_parsed_splits, possible_substrings_splits):
        rating = []
        for i in range(len(possible_parsed_splits)):
            num_substrings = len(possible_substrings_splits[i])
            not_parsed = 0
            for item in possible_parsed_splits[i]:
                if not item['date_obj']:
                    not_parsed += 1
            rating.append([num_substrings, not_parsed/num_substrings])
            best_index, best_rating = min(enumerate(rating), key=lambda p: (p[1][1], p[1][0]))
        return possible_parsed_splits[best_index], possible_substrings_splits[best_index]


    def split_by(self, item, original, splitter):
        if item.count(splitter) <= 2:
            return [[item.split(splitter), original.split(splitter)]]
        else:
            item_all_split = item.split(splitter)
            original_all_split = original.split(splitter)
            all_possible_splits = [[item_all_split, original_all_split]]
            for i in range(2, 4):
                item_partially_split = []
                original_partially_split = []
                for j in range(0, len(item_all_split), i):
                    item_join = splitter.join(item_all_split[j:j+i])
                    original_join = splitter.join(original_all_split[j:j+i])
                    item_partially_split.append(item_join)
                    original_partially_split.append(original_join)
                all_possible_splits.append([item_partially_split, original_partially_split])
            return all_possible_splits

    def split_if_not_parsed(self, item, original):
        splitters = [',', '،', '——', '—', '–', '.', ' ']
        possible_splits = []
        for splitter in splitters:
            if splitter in item and item.count(splitter) == original.count(splitter):
                possible_splits.extend(self.split_by(item, original, splitter))
        return possible_splits

    def parse_item(self, parser, item, translated_item, settings, parsed):
        item = item.replace('ngày', '')
        item = item.replace('am', '')
        pre_parsed_item = parser.get_date_data(item)
        is_relative = self.date_is_relative(translated_item)
        item, relative_base = self.set_relative_base(pre_parsed_item, item, parsed, is_relative,
                                                     settings=settings)
        if relative_base:
            parser._settings.RELATIVE_BASE = relative_base
            parsed_item = parser.get_date_data(item)
        else:
            parsed_item = pre_parsed_item
        parsed_item['is_relative'] = is_relative
        return parsed_item

    def parse_found_objects(self, parser, to_parse, original, translated, settings):
        parsed = []
        substrings = []
        for i, item in enumerate(to_parse):
            if len(item) > 2:
                parsed_item = self.parse_item(parser, item, translated[i], settings, parsed)
                if parsed_item['date_obj']:
                    parsed.append(parsed_item)
                    substrings.append(original[i].strip(' .,:()[]-'))
                    pass
                else:
                    possible_splits = self.split_if_not_parsed(item, original[i])
                    if possible_splits:
                        possible_parsed = []
                        possible_substrings = []
                        for split_translated, split_original in possible_splits:
                            current_parsed = []
                            current_substrings = []
                            if split_translated:
                                for j, jtem in enumerate(split_translated):
                                    if len(jtem) > 2:
                                        parsed_jtem = self.parse_item(parser, jtem, split_translated[j], settings,
                                                                      current_parsed)
                                        current_parsed.append(parsed_jtem)
                                        current_substrings.append(split_original[j].strip(' .,:()[]-'))
                            else:
                                pass
                            possible_parsed.append(current_parsed)
                            possible_substrings.append(current_substrings)
                        parsed_best, substrings_best = self.choose_best_split(possible_parsed, possible_substrings)
                        for k in range(len(parsed_best)):
                            if parsed_best[k]['date_obj']:
                                parsed.append(parsed_best[k])
                                substrings.append(substrings_best[k])
        return parsed, substrings

    def search_parse(self, shortname, text, settings=None):
        translated, original = self.search(shortname, text)
        if shortname not in ['vi', 'hu']:
            parser = DateDataParser(languages=['en'], settings=settings)
            parsed, substrings = self.parse_found_objects(parser=parser, to_parse=translated,
                                                          original=original, translated=translated, settings=settings)
        else:
            parser = DateDataParser(languages=[shortname], settings=settings)
            parsed, substrings = self.parse_found_objects(parser=parser, to_parse=original,
                                                          original=original, translated=translated, settings=settings)
        return list(zip(substrings, [i['date_obj'] for i in parsed]))
