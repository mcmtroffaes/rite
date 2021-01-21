import dataclasses
from abc import ABC, abstractmethod
from enum import Enum
from typing import Callable, List, Iterable, Iterator


class BaseText(ABC, Iterable[str]):
    """Rich text is a collection of strings with some additional formatting
    attached to it.
    """

    @abstractmethod
    def fmap_iter(self, funcs: Iterator[Callable[[str], str]]) -> "BaseText":
        """Apply the iterator *funcs* of functions consecutively to each string
        in the text and return the resulting rich text, retaining the original
        markup.
        """
        raise NotImplementedError


@dataclasses.dataclass(frozen=True)
class String(BaseText):
    value: str

    def __iter__(self) -> Iterator[str]:
        yield self.value

    def fmap_iter(self, funcs: Iterator[Callable[[str], str]]) -> "BaseText":
        return String(next(funcs)(self.value))


@dataclasses.dataclass(frozen=True)
class Join(BaseText):
    parts: List[BaseText]

    def __iter__(self) -> Iterator[str]:
        for part in self.parts:
            yield from part

    def fmap_iter(self, funcs: Iterator[Callable[[str], str]]) -> "BaseText":
        return Join([part.fmap_iter(funcs) for part in self.parts])


@dataclasses.dataclass(frozen=True)
class Protected(BaseText):
    """Protected against content changes through :meth:`functor_map_iter`."""
    child: BaseText

    def __iter__(self) -> Iterator[str]:
        yield from self.child

    def fmap_iter(self, funcs: Iterator[Callable[[str], str]]) -> "BaseText":
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

    def __iter__(self) -> Iterator[str]:
        yield from self.text

    def fmap_iter(self, funcs: Iterator[Callable[[str], str]]) -> "BaseText":
        return Tag(self.tag, self.text.fmap_iter(funcs))
