import string
from functools import singledispatch
from itertools import repeat, takewhile
from typing import Callable, TypeVar, List, Optional, Iterator, Iterable

from rite.richtext import BaseText, String

T = TypeVar('T')


@singledispatch
def text_fmap_iter(text: BaseText, funcs: Iterator[Callable[[str], str]]
                   ) -> BaseText:
    return text.replace(text_fmap_iter(child, funcs) for child in text)


@text_fmap_iter.register(String)
def _text_fmap_iter_string(text: String, funcs: Iterator[Callable[[str], str]]
                           ) -> BaseText:
    return String(next(funcs)(text.value))


def text_fmap(func: Callable[[str], str], text: BaseText) -> BaseText:
    return text_fmap_iter(text, repeat(func))


@singledispatch
def text_iter(text: BaseText) -> Iterable[str]:
    for child in text:
        yield from text_iter(child)


@text_iter.register(String)
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
    return text_fmap_iter(text, funcs())


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

    return text_fmap_iter(text, funcs())


_punctuation_chars = tuple(char for char in string.punctuation)


def list_join(
        children: List[T],
        sep: Optional[T] = None,
        sep2: Optional[T] = None,
        last_sep: Optional[T] = None,
        other: Optional[T] = None
        ) -> List[T]:
    if sep is None or not children:
        return children
    elif len(children) == 1:
        return [children[0]]
    elif len(children) == 2:
        return [children[0], sep2 if sep2 is not None else sep, children[1]]
    elif other is None:
        p1 = [text for child in children[:-2] for text in [child, sep]]
        p2 = [children[-2], last_sep if last_sep is not None else sep,
              children[-1]]
        return p1 + p2
    else:
        return [children[0], other]
