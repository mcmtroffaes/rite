import dataclasses
from abc import ABC, abstractmethod
from enum import Enum
from typing import Callable, List, TypeVar, Iterable, Iterator

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
class Protected(BaseText):
    """Protected against content changes through :meth:`functor_map_iter`."""
    child: BaseText

    def map_iter(self, funcs: Iterator[Callable[[str], T]]) -> Iterable[T]:
        yield from self.child.map_iter(funcs)

    def functor_map_iter(
            self, funcs: Iterator[Callable[[str], str]]) -> "BaseText":
        return self


class TagType(Enum):
    """Rich text tags. Values are html tags."""
    EMPHASIS = 'em'
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
