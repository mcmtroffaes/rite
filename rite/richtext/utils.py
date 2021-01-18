from itertools import repeat, takewhile
from typing import Callable, TypeVar, Iterable, List, Optional, Iterator

from rite.richtext import BaseText

T = TypeVar('T')


def text_map(text: BaseText, func: Callable[[str], T]) -> Iterable[T]:
    return text.map_iter(repeat(func))


def text_functor_map(
        text: BaseText, func: Callable[[str], str]) -> BaseText:
    return text.functor_map_iter(repeat(func))


def text_strings(text: BaseText) -> Iterable[str]:
    return text_map(text, lambda x: x)


def text_raw(text: BaseText) -> str:
    return ''.join(text_strings(text))


def text_is_empty(text: BaseText) -> bool:
    return not any(text_map(text, bool))


def text_is_upper(text: BaseText) -> bool:
    return all(text_map(text, str.isupper))


def text_is_lower(text: BaseText) -> bool:
    return all(text_map(text, str.islower))


def text_upper(text: BaseText) -> BaseText:
    return text_functor_map(text, str.upper)


def text_lower(text: BaseText) -> BaseText:
    return text_functor_map(text, str.lower)


def text_capitalize(text: BaseText) -> BaseText:
    def funcs() -> Iterator[Callable[[str], str]]:
        # iterate until a non-empty string is found
        for _ in takewhile(lambda x: not x, text_strings(text)):
            yield lambda x: x
        # non-empty string is found! capitalize it
        yield str.capitalize
        # convert the rest to lower case
        yield from repeat(str.lower)
    return text.functor_map_iter(funcs())


def text_capfirst(text: BaseText) -> BaseText:
    def _capfirst(value: str) -> str:
        assert value  # this is guaranteed by the funcs code below
        return value[0].upper() + value[1:]

    def funcs() -> Iterator[Callable[[str], str]]:
        # iterate until a non-empty string is found
        for _ in takewhile(lambda x: not x, text_strings(text)):
            yield lambda x: x
        # non-empty string is found! capitalize first character
        yield _capfirst
        # keep the rest as is
        yield from repeat(lambda x: x)

    return text.functor_map_iter(funcs())


def list_join(
        sep: T,
        parts: List[T],
        sep2: Optional[T] = None,
        last_sep: Optional[T] = None,
        other: Optional[T] = None
        ) -> List[T]:
    if not parts:
        return []
    elif len(parts) == 1:
        return [parts[0]]
    elif len(parts) == 2:
        return [parts[0], sep2 if sep2 is not None else sep, parts[1]]
    elif other is None:
        p1 = [text for part in parts[:-2] for text in [part, sep]]
        p2 = [parts[-2], last_sep if last_sep is not None else sep, parts[-1]]
        return p1 + p2
    else:
        return [parts[0], other]
