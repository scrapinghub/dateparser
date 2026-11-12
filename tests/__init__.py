from __future__ import annotations

from functools import lru_cache
from typing import TYPE_CHECKING, Any
from unittest import TestCase

import regex

if TYPE_CHECKING:
    from collections.abc import Iterable
    from unittest.mock import _patch


@lru_cache(maxsize=1)
def digits_unknown_to_int() -> tuple[str, ...]:
    """Characters that the regex module reads as digits but ``int()`` rejects,
    because the regex module knows digits that were added to Unicode after the
    Unicode version of this Python. There are none if this Python is at least as
    recent as the regex module."""
    characters = "".join(map(chr, range(0x110000)))
    return tuple(
        character
        for character in regex.findall(r"\d", characters)
        if not character.isdecimal()
    )


class BaseTestCase(TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.__patches: list[_patch[Any]] = []

        self.error: object = NotImplemented

    def add_patch(self, patch: _patch[Any]) -> None:
        patch.start()
        self.__patches.append(patch)

    def tearDown(self) -> None:
        super().tearDown()
        for patch in reversed(self.__patches):
            patch.stop()

    def then_error_was_raised(
        self,
        error_cls: type[BaseException],
        allowed_substrings: Iterable[str] = (),
    ) -> None:
        self.assertIsInstance(self.error, error_cls)
        self.assertTrue(
            any(mesg in str(self.error) for mesg in allowed_substrings),
            f"Didn't found any of the expected messages ({allowed_substrings!r}) -- message was: {self.error!r}",
        )
