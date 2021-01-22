import sys
from typing import TypeVar, Optional, List
if sys.version_info >= (3, 8):
    from typing import Protocol
else:
    from typing_extensions import Protocol

from rite.richtext import (
    BaseText, String, Join, Rich, Style,
    Semantics, FontSize, FontStyle, FontVariant, Color, TextAlign,
)
from rite.richtext.utils import (
    list_join, text_capfirst, text_lower, text_upper, text_capitalize,
)

Data = TypeVar('Data', contravariant=True)


class Node(Protocol[Data]):
    """A node is any object that can convert data into rich text."""
    def __call__(self, data: Data) -> BaseText:
        pass  # pragma: no cover


def str_(value: str) -> Node[Data]:
    """A plain string node."""
    def fmt(data: Data) -> BaseText:
        return String(value)
    return fmt


def join(children: List[Node[Data]],
         sep: Optional[BaseText] = None,
         sep2: Optional[BaseText] = None,
         last_sep: Optional[BaseText] = None,
         other: Optional[BaseText] = None
         ) -> Node[Data]:
    """A node which joins its *children* with the given separators."""
    def fmt(data: Data) -> BaseText:
        return Join(list_join(
            [child(data) for child in children],
            sep=sep, sep2=sep2, last_sep=last_sep, other=other))
    return fmt


def rich(
        child: Node[Data],
        semantics: Optional[Semantics] = None,
        font_size: FontSize = FontSize.MEDIUM,
        font_family: Optional[str] = None,
        font_style: FontStyle = FontStyle.NORMAL,
        font_weight: int = 400,
        font_variant: FontVariant = FontVariant.NORMAL,
        color: Optional[Color] = None,
        background_color: Optional[Color] = None,
        text_align: Optional[TextAlign] = None) -> Node[Data]:
    """A node which adds a tag to its child."""
    def fmt(data: Data) -> BaseText:
        return Rich(child=child(data), style=Style(
            semantics=semantics,
            font_size=font_size,
            font_family=font_family,
            font_style=font_style,
            font_weight=font_weight,
            font_variant=font_variant,
            color=color,
            background_color=background_color,
            text_align=text_align,
        ))
    return fmt


def capfirst(child: Node[Data]) -> Node[Data]:
    """A node which capitalizes the first letter of its child."""
    def fmt(data: Data) -> BaseText:
        return text_capfirst(child(data))
    return fmt


def capitalize(child: Node[Data]) -> Node[Data]:
    """A node which capitalizes all words of its child."""
    def fmt(data: Data) -> BaseText:
        return text_capitalize(child(data))
    return fmt


def lower(child: Node[Data]) -> Node[Data]:
    """A node which converts its child to lower case."""
    def fmt(data: Data) -> BaseText:
        return text_lower(child(data))
    return fmt


def upper(child: Node[Data]) -> Node[Data]:
    """A node which converts its child to upper case."""
    def fmt(data: Data) -> BaseText:
        return text_upper(child(data))
    return fmt
