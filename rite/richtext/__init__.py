import dataclasses
from abc import ABC, abstractmethod
from enum import Enum
from typing import List, Iterable, Iterator


class BaseText(ABC, Iterable["BaseText"]):
    """Rich text is a collection of strings with some additional formatting
    attached to it.
    """

    @abstractmethod
    def replace(self, children: Iterable["BaseText"]) -> "BaseText":
        raise NotImplementedError


@dataclasses.dataclass(frozen=True)
class String(BaseText):
    value: str

    def __iter__(self) -> Iterator["BaseText"]:
        return iter(())

    def replace(self, children: Iterable["BaseText"]) -> "BaseText":
        pass


@dataclasses.dataclass(frozen=True)
class Join(BaseText):
    children: List[BaseText]

    def __iter__(self) -> Iterator["BaseText"]:
        return iter(self.children)

    def replace(self, children: Iterable["BaseText"]) -> "BaseText":
        return dataclasses.replace(self, children=list(children))


@dataclasses.dataclass(frozen=True)
class Child(BaseText):
    child: BaseText

    def __iter__(self) -> Iterator["BaseText"]:
        yield self.child

    def replace(self, children: Iterable["BaseText"]) -> "BaseText":
        return dataclasses.replace(self, child=next(iter(children)))


class Semantics(Enum):
    """Semantic tags. Values are html tags."""
    STRONG = 'strong'
    EMPHASIS = 'em'
    MARK = 'mark'
    DELETED = 'del'
    INSERTED = 'ins'
    SUBSCRIPT = 'sub'
    SUPERSCRIPT = 'sup'
    CODE = 'code'
    UNARTICULATED = 'u'
    STRIKETHROUGH = 's'
    VARIABLE = 'var'
    H1 = 'h1'
    H2 = 'h2'
    H3 = 'h3'
    H4 = 'h4'
    H5 = 'h5'
    H6 = 'h6'
    PARAGRAPH = 'p'


class FontSizes(Enum):
    MEDIUM = 'medium'
    XX_SMALL = 'xx-small'
    X_SMALL = 'x-small'
    SMALL = 'small'
    LARGE = 'large'
    X_LARGE = 'x-large'
    XX_LARGE = 'xx-large'


class FontStyles(Enum):
    NORMAL = 'normal'
    ITALIC = 'italic'
    OBLIQUE = 'oblique'


class FontVariants(Enum):
    NORMAL = 'normal'
    SMALL_CAPS = 'small-caps'


@dataclasses.dataclass(frozen=True)
class Semantic(Child):
    semantic: Semantics


@dataclasses.dataclass(frozen=True)
class FontSize(Child):
    font_size: FontSizes


@dataclasses.dataclass(frozen=True)
class FontStyle(Child):
    font_style: FontStyles


@dataclasses.dataclass(frozen=True)
class FontVariant(Child):
    font_variant: FontVariants


@dataclasses.dataclass(frozen=True)
class FontWeight(Child):
    font_weight: int  #: 400 = normal, 700 = bold
