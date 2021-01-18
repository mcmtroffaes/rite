from functools import singledispatch
from typing import Iterable, Dict, Tuple

from rite.richtext import BaseText, Text, Tag, TagType
from rite.richtext.utils import text_map

rst_tags: Dict[TagType, Tuple[str, str]] = {
    TagType.EMPHASIS: ('*', '*'),
    TagType.STRONG: ('**', '**'),
    TagType.CODE: ('``', '``'),
    TagType.SUBSCRIPT: (':sub:`', '`'),
    TagType.SUPERSCRIPT: (':sup:`', '`'),
}

special_chars = r"\`*:"
special_trans = str.maketrans(
    dict((char, f'\\{char}') for char in special_chars))


def escape(value: str) -> str:
    return value.translate(special_trans)


@singledispatch
def render_rst(text: BaseText) -> Iterable[str]:
    yield from text_map(text, escape)


@render_rst.register(Tag)
def _tag(text: Tag) -> Iterable[str]:
    tags = rst_tags[text.tag]
    yield tags[0]
    yield from render_rst(text.text)
    yield tags[1]


@render_rst.register(Text)
def _text(text: Text) -> Iterable[str]:
    for part in text.parts:
        yield from render_rst(part)
