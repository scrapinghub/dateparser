from __future__ import annotations

from typing import TYPE_CHECKING, Any
from unittest import TestCase

if TYPE_CHECKING:
    from collections.abc import Iterable
    from unittest.mock import _patch


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
