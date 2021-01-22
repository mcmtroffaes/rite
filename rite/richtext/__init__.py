import dataclasses
from abc import ABC, abstractmethod
from enum import Enum
from typing import Callable, List, Iterable, Iterator, Optional


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
    PRE = 'pre'
    PARAGRAPH = 'p'


@dataclasses.dataclass
class Color:
    r: float
    g: float
    b: float


class FontSize(Enum):
    MEDIUM = 'medium'
    XX_SMALL = 'xx-small'
    X_SMALL = 'x-small'
    SMALL = 'small'
    LARGE = 'large'
    X_LARGE = 'x-large'
    XX_LARGE = 'xx-large'


class FontStyle(Enum):
    NORMAL = 'normal'
    ITALIC = 'italic'
    OBLIQUE = 'oblique'


class FontVariant(Enum):
    NORMAL = 'normal'
    SMALL_CAPS = 'small-caps'


class TextAlign(Enum):
    LEFT = 'left'
    RIGHT = 'right'
    CENTER = 'center'
    JUSTIFY = 'justify'


@dataclasses.dataclass(frozen=True)
class Style:
    semantics: Optional[Semantics] = None
    font_size: FontSize = FontSize.MEDIUM
    font_family: Optional[str] = None
    font_style: FontStyle = FontStyle.NORMAL
    font_weight: int = 400  #: 400 = normal, 700 = bold; >= 550 should be bold
    font_variant: FontVariant = FontVariant.NORMAL
    color: Optional[Color] = None
    background_color: Optional[Color] = None
    text_align: Optional[TextAlign] = None


@dataclasses.dataclass(frozen=True)
class Rich(BaseText):
    child: BaseText
    style: Style

    def __iter__(self) -> Iterator["BaseText"]:
        yield self.child

    def fmap_iter(self, funcs: Iterator[Callable[[str], str]]) -> "BaseText":
        return dataclasses.replace(self, child=self.child.fmap_iter(funcs))


class Symbol(Enum):
    LINEBREAK = 'br'
    HORIZONTAL_RULE = 'hr'


class SymbolText(BaseText):
    symbol: Symbol

    def __iter__(self) -> Iterator[BaseText]:
        return iter(())

    def fmap_iter(self, funcs: Iterator[Callable[[str], str]]) -> "BaseText":
        return self
