# coding: utf-8
import regex as re
from dateparser.languages.loader import LanguageDataLoader


class ExactLanguageSearch:
    def __init__(self):
        self.loader = LanguageDataLoader()
        self.language = None
        delimiter = '[\.\/\-]'
        year_full = '[1-9]{0,1}[0-9][0-9][0-9]'
        year_short = '[1-9]{0,1}[0-9]{0,1}[0-9][0-9]'
        month_full = '(?:0[1-9]|10|11|12)'
        month_short = '(?:0{0,1}[1-9]|10|11|12)'
        day_full = '[0-3][0-9]'
        day_short = '[0-3]{0,1}[0-9]'
        time_delimiter = '[:\s]'
        time_hours = '(?:0{0,1}[0-9]|1[0-9]|2[0-4])'
        time_min_sec = '[0-5][0-9]'
        time_microseconds = '.[0-9]{1,6}'

        date_patterns = ["{start}({year}{space1}{delimiter}{space2}{month}{space1}{delimiter}{space2}{day}){end}",  # (yy)yy/(m)m/(d)d
                         "{start}({year}{space1}{delimiter}{space2}{day}{space1}{delimiter}{space2}{month}){end}",  # (yy)yy/(d)d/(m)m
                         "{start}({day}{space1}{delimiter}{space2}{month}{space1}{delimiter}{space2}{year}){end}",  # (d)d/(m)m/(yy)yy
                         "{start}({month}{space1}{delimiter}{space2}{day}{space1}{delimiter}{space2}{year}){end}"]  # (m)m/(d)d/(yy)yy
        date_y = ["{start}({year}){end}"]
        date_md = ["{start}({month}{space1}{delimiter}{space2}{day}){end}",
                                    "{start}({day}{space1}{delimiter}{space2}{month}){end}"]
        self.reg_dict = dict()
        self.reg_dict['numeric_date_ymd'] = self.format_date_regs(date_patterns,
                                                                    year_short, month_short, day_short,
                                                                  delimiter, '', '')
        self.reg_dict['numeric_date_ymd_space_delimiter'] = self.format_date_regs(date_patterns,
                                                                    year_short, month_short, day_short,
                                                                                  delimiter, '\s', '\s')
        self.reg_dict['numeric_date_ymd_space'] = self.format_date_regs(date_patterns,
                                                                    year_short, month_short, day_short, '',  '\s', '')
        self.reg_dict['numeric_date_ymd_no_delimiter'] = self.format_date_regs(date_patterns,
                                                                    year_short, month_short, day_short, '', '', '')
        self.reg_dict['numeric_date_md'] = self.format_date_regs(date_md,
                                                                    '', month_short, day_short, delimiter,  '', '')
        self.reg_dict['numeric_date_y'] = self.format_date_regs(date_y,
                                                                 year_full, '', '', '', '', '')
        self.general = self.compile_general_regs(self.reg_dict)
        self.ordered_numeric = ['numeric_date_ymd', 'numeric_date_ymd_space_delimiter', 'numeric_date_ymd_space',
                                'numeric_date_ymd_no_delimiter', 'numeric_date_md', 'numeric_date_y']

    def get_current_language(self, shortname):
        self.language = self.loader.get_language(shortname)

    @staticmethod
    def format_date_regs(patterns, year, month, day, delimiter, space1, space2):
        formatted = []
        for pattern in patterns:
            formatted.append(pattern.format(
                year=year, month=month, day=day, delimiter=delimiter, space1=space1, space2=space2,
                start='(?:[^/0-9]|^)', end='(?:[^/0-9]|$)'
            ))
        return formatted

    @staticmethod
    def compile_general_regs(reg_dict):
        for key in reg_dict:
            reg_dict[key] = [re.compile(reg_exp) for reg_exp in reg_dict[key]]
        return reg_dict

    def get_specific_regs(self):
        pass

    @staticmethod
    def sort_found_objects_in_relative_order(found):
        return sorted(found, key=lambda x: (x[0], x[1]))

    # def unite_splitted_objects(self, found_inorder):
    #     return found_inorder

    def _search(self, text, langinfo):
        found = []
        search_text = text
        ln = len(search_text)
        for key in self.ordered_numeric:
            print(key)
            for reg in self.general[key]:
                if ln >= 4:
                    res = re.finditer(reg, search_text, overlapped=True)
                    res_list = [[i.start(), i.end(), i] for i in res]
                    found.extend(res_list)
                    print(res_list)
                    for obj in res_list:
                        search_text = search_text[:obj[0]]+' '*(obj[1]-obj[0])+search_text[obj[1]:]
                        ln -= (obj[1]-obj[0])
                        print(search_text)
                else:
                    break

        return self.sort_found_objects_in_relative_order(found)

    def final_search(self, shortname, text):
        self.get_current_language(shortname)
        found_objects = self._search(text, self.language)
        found_strings = []
        for obj in found_objects:
            found_strings.append(obj[2].group(1))
        return found_strings

