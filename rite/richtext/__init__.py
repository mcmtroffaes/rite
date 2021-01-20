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
    def __iter__(self) -> Iterable[str]:
        """Return all raw unformatted strings from the text."""
        raise NotImplementedError

    @abstractmethod
    def fmap(self, funcs: Iterator[Callable[[str], str]]) -> "BaseText":
        """Apply the iterator *funcs* of functions consecutively to each string
        in the text and return the resulting rich text, retaining the original
        markup.
        """
        raise NotImplementedError


@dataclasses.dataclass(frozen=True)
class String(BaseText):
    value: str

    def __iter__(self) -> Iterable[str]:
        yield self.value

    def fmap(self, funcs: Iterator[Callable[[str], str]]) -> "BaseText":
        return String(next(funcs)(self.value))


@dataclasses.dataclass(frozen=True)
class Text(BaseText):
    parts: List[BaseText]

    def __iter__(self) -> Iterable[str]:
        for part in self.parts:
            yield from part

    def fmap(self, funcs: Iterator[Callable[[str], str]]) -> "BaseText":
        return Text([part.fmap(funcs) for part in self.parts])


@dataclasses.dataclass(frozen=True)
class Protected(BaseText):
    """Protected against content changes through :meth:`functor_map_iter`."""
    child: BaseText

    def __iter__(self) -> Iterable[str]:
        yield from self.child

    def fmap(self, funcs: Iterator[Callable[[str], str]]) -> "BaseText":
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

    def __iter__(self) -> Iterable[str]:
        yield from self.text

    def fmap(self, funcs: Iterator[Callable[[str], str]]) -> "BaseText":
        return Tag(self.tag, self.text.fmap(funcs))
