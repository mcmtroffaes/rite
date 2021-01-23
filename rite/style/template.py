import sys
from typing import TypeVar, Optional, List
if sys.version_info >= (3, 8):
    from typing import Protocol
else:
    from typing_extensions import Protocol

from rite.richtext import (
    BaseText, String, Join, Semantics, FontSizes, FontStyles, FontVariants,
    Semantic, FontSize, FontStyle, FontVariant, FontWeight
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


def semantic(child: Node[Data], style: Semantics) -> Node[Data]:
    def fmt(data: Data) -> BaseText:
        return Semantic(child(data), style)
    return fmt


def font_size(child: Node[Data], style: FontSizes) -> Node[Data]:
    def fmt(data: Data) -> BaseText:
        return FontSize(child(data), style)
    return fmt


def font_style(child: Node[Data], style: FontStyles) -> Node[Data]:
    def fmt(data: Data) -> BaseText:
        return FontStyle(child(data), style)
    return fmt


def font_variant(child: Node[Data], style: FontVariants) -> Node[Data]:
    def fmt(data: Data) -> BaseText:
        return FontVariant(child(data), style)
    return fmt


def font_weight(child: Node[Data], style: int) -> Node[Data]:
    def fmt(data: Data) -> BaseText:
        return FontWeight(child(data), style)
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
