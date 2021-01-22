from functools import singledispatch
from typing import Iterable, Dict, Tuple, Optional

from rite.richtext import BaseText, Join, Rich, Semantics
from rite.richtext.utils import text_iter

markdown_tags: Dict[Semantics, Tuple[str, str]] = {
    Semantics.EMPHASIS: ('*', '*'),
    Semantics.STRONG: ('**', '**'),
    Semantics.CODE: ('`', '`'),
    Semantics.SUBSCRIPT: ('<sub>', '</sub>'),
    Semantics.SUPERSCRIPT: ('<sup>', '</sup>'),
}

# from https://enterprise.github.com/downloads/en/markdown-cheatsheet.pdf
special_chars = r"\`*_{}[]()#+-.!"
special_trans = str.maketrans(
    dict((char, f'\\{char}') for char in special_chars))


def escape(value: str) -> str:
    return value.translate(special_trans)


@singledispatch
def render_markdown(text: BaseText) -> Iterable[str]:
    yield from map(escape, text_iter(text))


@render_markdown.register(Rich)
def _tag(text: Rich) -> Iterable[str]:
    tags: Optional[Tuple[str, str]] = None
    if text.style.semantics is not None:
        tags = markdown_tags[text.style.semantics]
    if tags is not None:
        yield tags[0]
    yield from render_markdown(text.child)
    if tags is not None:
        yield tags[1]


@render_markdown.register(Join)
def _join(text: Join) -> Iterable[str]:
    for child in text.children:
        yield from render_markdown(child)
