import string
from typing import TypeVar, Protocol, Optional, List

from rite.richtext import BaseText, String, Text, Tag, TagType, text_map, text_raw
from rite.richtext import list_join, text_capfirst, text_lower, text_upper

Data = TypeVar('Data', contravariant=True)


class Node(Protocol[Data]):
    """A node is any object that can convert data into rich text."""
    def __call__(self, data: Data) -> BaseText:
        pass


def str_(value: str) -> Node[Data]:
    """A plain string node."""
    def fmt(data: Data) -> BaseText:
        return String(value)
    return fmt


def text(children: List[Node[Data]]) -> Node[Data]:
    """A node which joins its *children*."""
    def fmt(data: Data) -> BaseText:
        return Text([child(data) for child in children])
    return fmt


def join(sep: BaseText,
         children: List[Node[Data]],
         sep2: Optional[BaseText] = None,
         last_sep: Optional[BaseText] = None,
         other: Optional[BaseText] = None
         ) -> Node[Data]:
    """A node which joins its *children* with the given separators."""
    def fmt(data: Data) -> BaseText:
        return Text(list_join(
            sep, [child(data) for child in children],
            sep2=sep2, last_sep=last_sep, other=other))
    return fmt


def tag(tag_: TagType, child: Node[Data]) -> Node[Data]:
    """A node which adds a tag to its child."""
    def fmt(data: Data) -> BaseText:
        return Tag(tag=tag_, text=child(data))
    return fmt


def capfirst(child: Node[Data]) -> Node[Data]:
    """A node which capitalizes the first letter of its child."""
    def fmt(data: Data) -> BaseText:
        return text_capfirst(child(data))
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


def add_period(child: Node[Data]) -> Node[Data]:
    """A node which adds appends period to its child, if the child does not
    already end with a punctuation symbol.
    """
    chars = tuple(char for char in string.punctuation)

    def fmt(data: Data) -> BaseText:
        text = child(data)
        if not text_raw(text).endswith(chars):
            return Text([text, String(".")])
        else:
            return text
    return fmt
