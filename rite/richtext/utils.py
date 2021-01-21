import string
from functools import singledispatch
from itertools import repeat, takewhile
from typing import Callable, TypeVar, List, Optional, Iterator, Iterable

from rite.richtext import BaseText, String

T = TypeVar('T')


def text_fmap(func: Callable[[str], str], text: BaseText) -> BaseText:
    return text.fmap_iter(repeat(func))


@singledispatch
def text_iter(text: BaseText) -> Iterable[str]:
    for child in text:
        yield from text_iter(child)


@text_iter.register
def _text_iter_string(text: String) -> Iterable[str]:
    yield text.value


def text_raw(text: BaseText) -> str:
    return ''.join(text_iter(text))


def text_is_empty(text: BaseText) -> bool:
    return not any(map(bool, text_iter(text)))


def text_is_upper(text: BaseText) -> bool:
    return text_raw(text).isupper()


def text_is_lower(text: BaseText) -> bool:
    return text_raw(text).islower()


def text_upper(text: BaseText) -> BaseText:
    return text_fmap(str.upper, text)


def text_lower(text: BaseText) -> BaseText:
    return text_fmap(str.lower, text)


def text_capitalize(text: BaseText) -> BaseText:
    def funcs() -> Iterator[Callable[[str], str]]:
        # iterate until a non-empty string is found
        for _ in takewhile(lambda x: not x, text_iter(text)):
            yield lambda x: x
        # non-empty string is found! capitalize it
        yield str.capitalize
        # convert the rest to lower case
        yield from repeat(str.lower)
    return text.fmap_iter(funcs())


def text_capfirst(text: BaseText) -> BaseText:
    def _capfirst(value: str) -> str:
        assert value  # this is guaranteed by the funcs code below
        return value[0].upper() + value[1:]

    def funcs() -> Iterator[Callable[[str], str]]:
        # iterate until a non-empty string is found
        for _ in takewhile(lambda x: not x, text_iter(text)):
            yield lambda x: x
        # non-empty string is found! capitalize first character
        yield _capfirst
        # keep the rest as is
        yield from repeat(lambda x: x)

    return text.fmap_iter(funcs())


_punctuation_chars = tuple(char for char in string.punctuation)


def list_join(
        parts: List[T],
        sep: Optional[T] = None,
        sep2: Optional[T] = None,
        last_sep: Optional[T] = None,
        other: Optional[T] = None
        ) -> List[T]:
    if sep is None or not parts:
        return parts
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
