import contextlib
import datetime
import io
import tempfile
from collections.abc import Iterator
from typing import List, TypeVar

import atheris

T = TypeVar("T")


class EnhancedFuzzedDataProvider(atheris.FuzzedDataProvider):  # type: ignore[misc]
    def ConsumeRandomBytes(self) -> bytes:
        result: bytes = self.ConsumeBytes(
            self.ConsumeIntInRange(0, self.remaining_bytes())
        )
        return result

    def ConsumeRandomString(self) -> str:
        result: str = self.ConsumeUnicodeNoSurrogates(
            self.ConsumeIntInRange(0, self.remaining_bytes())
        )
        return result

    def ConsumeRemainingString(self) -> str:
        result: str = self.ConsumeUnicodeNoSurrogates(self.remaining_bytes())
        return result

    def ConsumeRemainingBytes(self) -> bytes:
        result: bytes = self.ConsumeBytes(self.remaining_bytes())
        return result

    def ConsumeSublist(self, source: List[T]) -> List[T]:
        """
        Returns a shuffled sub-list of the given list of len [1, len(source)]
        """
        chosen = [elem for elem in source if self.ConsumeBool()]

        # Shuffle
        for i in range(len(chosen) - 1, 1, -1):
            j = self.ConsumeIntInRange(0, i)
            chosen[i], chosen[j] = chosen[j], chosen[i]

        return chosen or [self.PickValueInList(source)]

    def ConsumeDate(self) -> datetime.datetime:
        try:
            return datetime.datetime.fromtimestamp(self.ConsumeFloat())
        except (OverflowError, OSError, ValueError):
            return datetime.datetime(year=1970, month=1, day=1)

    @contextlib.contextmanager
    def ConsumeMemoryFile(
        self, all_data: bool = False, as_bytes: bool = True
    ) -> Iterator[io.BytesIO | io.StringIO]:
        file: io.BytesIO | io.StringIO
        if as_bytes:
            file = io.BytesIO(
                self.ConsumeRemainingBytes() if all_data else self.ConsumeRandomBytes()
            )
        else:
            file = io.StringIO(
                self.ConsumeRemainingString()
                if all_data
                else self.ConsumeRandomString()
            )
        yield file
        file.close()

    @contextlib.contextmanager
    def ConsumeTemporaryFile(
        self, suffix: str, all_data: bool = False, as_bytes: bool = True
    ) -> Iterator[str]:
        file_data: bytes | str
        if all_data:
            file_data = (
                self.ConsumeRemainingBytes()
                if as_bytes
                else self.ConsumeRemainingString()
            )
        else:
            file_data = (
                self.ConsumeRandomBytes() if as_bytes else self.ConsumeRandomString()
            )

        mode = "w+b" if as_bytes else "w+"
        tfile = tempfile.NamedTemporaryFile(mode=mode, suffix=suffix)
        tfile.write(file_data)
        tfile.seek(0)
        tfile.flush()
        yield tfile.name
        tfile.close()
