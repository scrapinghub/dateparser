import re
from typing import Any

from dateparser.conf import Settings, apply_settings
from dateparser.languages.locale import Locale
from dateparser.search.detection import BaseLanguageDetector
from dateparser.utils import normalize_unicode

# Hiragana and katakana, except the middle dot, which Chinese also uses.
_KANA = re.compile(r"[\u3041-\u3096\u30a1-\u30fa\u30fc-\u30ff]")


class FullTextLanguageDetector(BaseLanguageDetector):
    def __init__(self, languages: list[Locale]) -> None:
        super(BaseLanguageDetector, self).__init__()
        self.languages = languages[:]
        self.language_unique_chars: list[set[str]] = []
        self.language_chars: list[set[str]] = []

    def get_unique_characters(self, settings: Settings) -> None:
        settings = settings.replace(NORMALIZE=False)

        for language in self.languages:
            chars = language.get_wordchars_for_detection(settings=settings)
            self.language_chars.append(chars)

        for char_set in self.language_chars:
            unique_chars = char_set
            for other_char_set in self.language_chars:
                if other_char_set != char_set:
                    unique_chars = unique_chars - other_char_set
            self.language_unique_chars.append(unique_chars)

    def character_check(self, date_string: str, settings: Settings) -> None:
        date_string_set = set(date_string.lower())
        symbol_set = {
            "0",
            "1",
            "2",
            "3",
            "4",
            "5",
            "6",
            "7",
            "8",
            "9",
            " ",
            "/",
            "-",
            ")",
            "(",
            ".",
            ":",
            "\\",
            ",",
            "'",
        }
        if date_string_set & symbol_set == date_string_set:
            self.languages = [self.languages[0]]
            return
        if _KANA.search(date_string):
            # Chinese words are also Japanese ones, e.g. 後天 ("acquired").
            self.languages = [
                language
                for language in self.languages
                if language.shortname.split("-")[0] not in {"zh", "yue"}
            ] or self.languages
        self.get_unique_characters(settings=settings)
        for i in range(len(self.languages)):
            for char in self.language_unique_chars[i]:
                if char.lower() in date_string.lower():
                    self.languages = [self.languages[i]]
                    return
        indices_to_pop = [
            i
            for i in range(len(self.languages))
            if len(date_string_set & self.language_chars[i]) == 0
        ]
        self.languages = [
            i for j, i in enumerate(self.languages) if j not in indices_to_pop
        ]

    @apply_settings
    def _best_language(
        self, date_string: str, settings: Settings | dict[str, Any] | None = None
    ) -> str | None:
        assert isinstance(settings, Settings)
        self.character_check(date_string, settings)
        date_string = normalize_unicode(date_string.lower())
        if len(self.languages) == 1:
            return self.languages[0].shortname
        applicable_languages = []
        for language in self.languages:
            for strip_timezone in (False, True):
                num_words = language.count_applicability(
                    date_string, strip_timezone=strip_timezone, settings=settings
                )
                if num_words[0] > 0 or num_words[1] > 0:
                    # On a tie, prefer the language that matches more words
                    # without letter variants, so that e.g. Arabic text is not
                    # taken for Persian.
                    native_num_words = (
                        num_words
                        if language._native is language
                        else language._native.count_applicability(
                            date_string,
                            strip_timezone=strip_timezone,
                            settings=settings,
                        )
                    )
                    applicable_languages.append(
                        (
                            language.shortname,
                            (*num_words[:2], *native_num_words[:2]),
                            num_words[2],
                        )
                    )
                    break
        if not applicable_languages:
            return None
        # Bare-number hits only break ties between languages with word hits;
        # otherwise every language that maps a number to a month would beat
        # the first language on text like "2018-10-17T00:00:00".
        has_words = any(num_words[0] for _, num_words, _ in applicable_languages)
        return max(
            applicable_languages,
            key=lambda p: (p[1], p[2]) if has_words else p[1],
        )[0]
