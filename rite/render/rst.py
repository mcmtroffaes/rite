from functools import singledispatch
from typing import Iterable, Dict, Tuple, Optional

from rite.richtext import (
    BaseText, Join, Semantics, FontStyles, Child,
    Semantic, FontStyle, FontWeight
)
from rite.richtext.utils import text_iter

rst_tags: Dict[Semantics, Tuple[str, str]] = {
    Semantics.EMPHASIS: ('*', '*'),
    Semantics.STRONG: ('**', '**'),
    Semantics.SUBSCRIPT: (':sub:`', '`'),
    Semantics.SUPERSCRIPT: (':sup:`', '`'),
    Semantics.CODE: ('``', '``'),
}

special_chars = r"\`*:"
special_trans = str.maketrans(
    dict((char, f'\\{char}') for char in special_chars))


def escape(value: str) -> str:
    return value.translate(special_trans)


def style_rst_tags(text: Child) -> Optional[Tuple[str, str]]:
    if isinstance(text, Semantic):
        try:
            return rst_tags[text.semantic]
        except KeyError:
            pass
    if isinstance(text, FontStyle) and text.font_style == FontStyles.ITALIC:
        return '*', '*'
    if isinstance(text, FontWeight) and text.font_weight >= 550:
        return '**', '**'
    return None


@singledispatch
def render_rst(text: BaseText) -> Iterable[str]:
    yield from map(escape, text_iter(text))


@render_rst.register(Child)
def _rich(text: Child) -> Iterable[str]:
    tags = style_rst_tags(text)
    if tags is not None:
        yield tags[0]
    yield from render_rst(text.child)
    if tags is not None:
        yield tags[1]


@render_rst.register(Join)
def _join(text: Join) -> Iterable[str]:
    for child in text.children:
        yield from render_rst(child)
