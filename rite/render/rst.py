from functools import singledispatch
from typing import Iterable, Dict, Tuple, Optional

from rite.richtext import BaseText, Join, Rich, Semantics, Style, FontStyle
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


def style_rst_tags(style: Style) -> Optional[Tuple[str, str]]:
    if style.semantics is not None:
        try:
            return rst_tags[style.semantics]
        except KeyError:
            pass
    if style.font_style != FontStyle.NORMAL:
        if style.font_style == FontStyle.ITALIC:
            return '*', '*'
    if style.font_weight >= 550:
        return '**', '**'
    return None


@singledispatch
def render_rst(text: BaseText) -> Iterable[str]:
    yield from map(escape, text_iter(text))


@render_rst.register(Rich)
def _rich(text: Rich) -> Iterable[str]:
    tags = style_rst_tags(text.style)
    if tags is not None:
        yield tags[0]
    yield from render_rst(text.child)
    if tags is not None:
        yield tags[1]


@render_rst.register(Join)
def _join(text: Join) -> Iterable[str]:
    for child in text.children:
        yield from render_rst(child)
