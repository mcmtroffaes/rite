import dataclasses
from abc import ABC, abstractmethod
from enum import Enum
from typing import Callable, List, Iterable, Iterator


class BaseText(ABC, Iterable["BaseText"]):
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

    def __iter__(self) -> Iterator["BaseText"]:
        return iter(())

    def fmap_iter(self, funcs: Iterator[Callable[[str], str]]) -> "BaseText":
        return String(next(funcs)(self.value))


@dataclasses.dataclass(frozen=True)
class Join(BaseText):
    children: List[BaseText]

    def __iter__(self) -> Iterator["BaseText"]:
        return iter(self.children)

    def fmap_iter(self, funcs: Iterator[Callable[[str], str]]) -> "BaseText":
        return Join([child.fmap_iter(funcs) for child in self.children])


@dataclasses.dataclass(frozen=True)
class Protected(BaseText):
    """Protected against content changes through :meth:`functor_map_iter`."""
    child: BaseText

    def __iter__(self) -> Iterator["BaseText"]:
        yield self.child

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
    child: BaseText

    def __iter__(self) -> Iterator["BaseText"]:
        yield self.child

    def fmap_iter(self, funcs: Iterator[Callable[[str], str]]) -> "BaseText":
        return Tag(self.tag, self.child.fmap_iter(funcs))
