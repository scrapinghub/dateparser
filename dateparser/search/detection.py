from collections.abc import Callable, Iterator
from functools import wraps
from typing import TYPE_CHECKING, Concatenate, ParamSpec, TypeVar

if TYPE_CHECKING:
    from dateparser.conf import Settings
    from dateparser.languages.locale import Locale

_S = TypeVar("_S", bound="BaseLanguageDetector")
_P = ParamSpec("_P")


def _restore_languages_on_generator_exit(
    method: Callable[Concatenate[_S, _P], Iterator["Locale"]],
) -> Callable[Concatenate[_S, _P], Iterator["Locale"]]:
    @wraps(method)
    def wrapped(self: _S, /, *args: _P.args, **kwargs: _P.kwargs) -> Iterator["Locale"]:
        stored_languages = self.languages[:]
        for language in method(self, *args, **kwargs):
            yield language
        else:
            self.languages[:] = stored_languages

    return wrapped


class BaseLanguageDetector:
    def __init__(self, languages: list["Locale"]) -> None:
        self.languages = languages[:]

    @_restore_languages_on_generator_exit
    def iterate_applicable_languages(
        self,
        date_string: str,
        settings: "Settings | None" = None,
        modify: bool = False,
    ) -> Iterator["Locale"]:
        languages = self.languages if modify else self.languages[:]
        yield from self._filter_languages(date_string, languages, settings)

    @staticmethod
    def _filter_languages(
        date_string: str, languages: list["Locale"], settings: "Settings | None" = None
    ) -> Iterator["Locale"]:
        while languages:
            language = languages[0]
            if language.is_applicable(
                date_string, strip_timezone=False, settings=settings
            ):
                yield language
            elif language.is_applicable(
                date_string, strip_timezone=True, settings=settings
            ):
                yield language

            languages.pop(0)


class AutoDetectLanguage(BaseLanguageDetector):
    def __init__(
        self, languages: list["Locale"], allow_redetection: bool = False
    ) -> None:
        super().__init__(languages=languages[:])
        self.language_pool = languages[:]
        self.allow_redetection = allow_redetection

    @_restore_languages_on_generator_exit
    def iterate_applicable_languages(  # type: ignore[override]
        self,
        date_string: str,
        modify: bool = False,
        settings: "Settings | None" = None,
    ) -> Iterator["Locale"]:
        languages = self.languages if modify else self.languages[:]
        initial_languages = languages[:]
        yield from self._filter_languages(date_string, languages, settings=settings)

        if not self.allow_redetection:
            return

        # Try languages that was not tried before with this date_string
        languages = [
            language
            for language in self.language_pool
            if language not in initial_languages
        ]
        if modify:
            self.languages = languages

        yield from self._filter_languages(date_string, languages, settings=settings)


class ExactLanguages(BaseLanguageDetector):
    def __init__(self, languages: list["Locale"] | None) -> None:
        if languages is None:
            raise ValueError("language cannot be None for ExactLanguages")
        super().__init__(languages=languages)

    @_restore_languages_on_generator_exit
    def iterate_applicable_languages(  # type: ignore[override]
        self,
        date_string: str,
        modify: bool = False,
        settings: "Settings | None" = None,
    ) -> Iterator["Locale"]:
        yield from super().iterate_applicable_languages(
            date_string, modify=False, settings=settings
        )
