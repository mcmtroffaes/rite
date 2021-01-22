from functools import singledispatch
from typing import Iterable, Dict, Tuple, Optional

from rite.richtext import BaseText, Join, Rich, Semantics
from rite.richtext.utils import text_iter

rst_tags: Dict[Semantics, Tuple[str, str]] = {
    Semantics.EMPHASIS: ('*', '*'),
    Semantics.STRONG: ('**', '**'),
    Semantics.CODE: ('``', '``'),
    Semantics.STRIKETHROUGH: ('~~', '~~'),
    Semantics.SUBSCRIPT: (':sub:`', '`'),
    Semantics.SUPERSCRIPT: (':sup:`', '`'),
}

special_chars = r"\`*:"
special_trans = str.maketrans(
    dict((char, f'\\{char}') for char in special_chars))


def escape(value: str) -> str:
    return value.translate(special_trans)


@singledispatch
def render_rst(text: BaseText) -> Iterable[str]:
    yield from map(escape, text_iter(text))


@render_rst.register(Rich)
def _tag(text: Rich) -> Iterable[str]:
    tags: Optional[Tuple[str, str]] = None
    if text.style.semantics is not None:
        tags = rst_tags.get(text.style.semantics)
    if tags is not None:
        yield tags[0]
    yield from render_rst(text.child)
    if tags is not None:
        yield tags[1]


@render_rst.register(Join)
def _join(text: Join) -> Iterable[str]:
    for child in text.children:
        yield from render_rst(child)
