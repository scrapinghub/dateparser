from collections.abc import Callable, Iterable
from typing import Any, TypeVar

_F = TypeVar("_F", bound=Callable[..., Any])

class param:
    def __init__(self, *args: Any, **kwargs: Any) -> None: ...

class parameterized:
    @classmethod
    def expand(
        cls,
        input: Iterable[Any],
        name_func: Callable[..., str] | None = None,
        doc_func: Callable[..., str | None] | None = None,
        skip_on_empty: bool = False,
        namespace: dict[str, Any] | None = None,
        **legacy: Any,
    ) -> Callable[[_F], _F]: ...
