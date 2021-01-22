from functools import singledispatch
from typing import Iterable, Dict, Tuple, Optional

from rite.richtext import BaseText, Join, Rich, Semantics, Style, FontStyle
from rite.richtext.utils import text_iter

markdown_tags: Dict[Semantics, Tuple[str, str]] = {
    Semantics.EMPHASIS: ('*', '*'),
    Semantics.STRONG: ('**', '**'),
    Semantics.MARK: ('**', '**'),
    Semantics.DELETED: ('~~', '~~'),
    Semantics.INSERTED: ('_', '_'),
    Semantics.SUBSCRIPT: ('<sub>', '</sub>'),
    Semantics.SUPERSCRIPT: ('<sup>', '</sup>'),
    Semantics.CODE: ('`', '`'),
    Semantics.UNARTICULATED: ('_', '_'),
    Semantics.STRIKETHROUGH: ('~~', '~~'),
    Semantics.VARIABLE: ('*', '*'),
}

# from https://enterprise.github.com/downloads/en/markdown-cheatsheet.pdf
special_chars = r"\`*_{}[]()#+-.!"
special_trans = str.maketrans(
    dict((char, f'\\{char}') for char in special_chars))


def escape(value: str) -> str:
    return value.translate(special_trans)


def style_markdown_tags(style: Style) -> Optional[Tuple[str, str]]:
    if style.semantics is not None:
        try:
            return markdown_tags[style.semantics]
        except KeyError:
            pass
    if style.font_style != FontStyle.NORMAL:
        if style.font_style == FontStyle.ITALIC:
            return '*', '*'
    if style.font_weight >= 550:
        return '**', '**'
    return None


@singledispatch
def render_markdown(text: BaseText) -> Iterable[str]:
    yield from map(escape, text_iter(text))


@render_markdown.register(Rich)
def _rich(text: Rich) -> Iterable[str]:
    tags = style_markdown_tags(text.style)
    if tags is not None:
        yield tags[0]
    yield from render_markdown(text.child)
    if tags is not None:
        yield tags[1]


@render_markdown.register(Join)
def _join(text: Join) -> Iterable[str]:
    for child in text.children:
        yield from render_markdown(child)
