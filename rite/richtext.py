import dataclasses
from abc import ABC, abstractmethod
from enum import Enum
from itertools import repeat
from typing import Callable, List, Optional, TypeVar, Iterable, Iterator

T = TypeVar('T')


class BaseText(ABC):
    """Rich text is a collection of strings with some additional formatting
    attached to it.
    """

    @abstractmethod
    def map_iter(self, funcs: Iterator[Callable[[str], T]]) -> Iterable[T]:
        """Apply iterator *funcs* of functions consecutively to each string
        in the text and return the results.
        """
        raise NotImplementedError

    @abstractmethod
    def functor_map_iter(
            self, funcs: Iterator[Callable[[str], str]]) -> "BaseText":
        """Apply the iterator *funcs* of functions consecutively to each string
        in the text and return the resulting rich text, retaining the original
        markup.
        """
        raise NotImplementedError


@dataclasses.dataclass(frozen=True)
class String(BaseText):
    value: str

    def map_iter(self, funcs: Iterator[Callable[[str], T]]) -> Iterable[T]:
        yield next(funcs)(self.value)

    def functor_map_iter(
            self, funcs: Iterator[Callable[[str], str]]) -> "BaseText":
        return String(next(funcs)(self.value))


class TagType(Enum):
    """Rich text tags. Values are html tags."""
    EMPHASIZE = 'em'
    STRONG = 'strong'
    CODE = 'code'
    SUPERSCRIPT = 'sup'
    SUBSCRIPT = 'sub'


@dataclasses.dataclass(frozen=True)
class Tag(BaseText):
    tag: TagType
    text: BaseText

    def map_iter(self, funcs: Iterator[Callable[[str], T]]) -> Iterable[T]:
        yield from self.text.map_iter(funcs)

    def functor_map_iter(
            self, funcs: Iterator[Callable[[str], str]]) -> "BaseText":
        return Tag(self.tag, self.text.functor_map_iter(funcs))


@dataclasses.dataclass(frozen=True)
class Text(BaseText):
    parts: List[BaseText]

    def map_iter(self, funcs: Iterator[Callable[[str], T]]) -> Iterable[T]:
        for part in self.parts:
            yield from part.map_iter(funcs)

    def functor_map_iter(
            self, funcs: Iterator[Callable[[str], str]]) -> "BaseText":
        return Text([part.functor_map_iter(funcs) for part in self.parts])


@dataclasses.dataclass(frozen=True)
class Protected(Text):
    """Like text but protected against content changes through
    :meth:`functor_map_iter`.
    """

    def functor_map_iter(
            self, funcs: Iterator[Callable[[str], str]]) -> "BaseText":
        return self


def text_map(text: BaseText, func: Callable[[str], T]) -> Iterable[T]:
    return text.map_iter(repeat(func))


def text_functor_map(
        text: BaseText, func: Callable[[str], str]) -> BaseText:
    return text.functor_map_iter(repeat(func))


def text_raw(text: BaseText) -> str:
    return ''.join(text_map(text, lambda x: x))


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
        for non_empty in text.map_iter(repeat(bool)):
            if not non_empty:
                yield lambda x: x
            else:
                break
        # non-empty string is found! capitalize it
        yield str.capitalize
        # convert the rest to lower case
        yield from repeat(str.lower)
    return text.functor_map_iter(funcs())


def text_capfirst(text: BaseText) -> BaseText:
    def _capfirst(value: str) -> str:
        return value[0].upper() + value[1]

    def funcs() -> Iterator[Callable[[str], str]]:
        # iterate until a non-empty string is found
        for non_empty in text.map_iter(repeat(bool)):
            if not non_empty:
                yield lambda x: x
            else:
                break
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
