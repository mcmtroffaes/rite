from functools import singledispatch
from typing import Iterable, Dict, Tuple, Optional

from rite.richtext import (
    BaseText, Join, Semantics, FontStyles, Child, Semantic, FontStyle,
    FontWeight
)
from rite.richtext.utils import iter_strings

markdown_tags: Dict[Semantics, Tuple[str, str]] = {
    Semantics.EMPHASIS: ('*', '*'),
    Semantics.STRONG: ('**', '**'),
    Semantics.SUBSCRIPT: ('<sub>', '</sub>'),
    Semantics.SUPERSCRIPT: ('<sup>', '</sup>'),
    Semantics.CODE: ('`', '`'),
    Semantics.STRIKETHROUGH: ('~~', '~~'),
    Semantics.H1: ('\n\n# ', '\n\n'),
    Semantics.H2: ('\n\n## ', '\n\n'),
    Semantics.H3: ('\n\n### ', '\n\n'),
    Semantics.H4: ('\n\n#### ', '\n\n'),
    Semantics.H5: ('\n\n##### ', '\n\n'),
    Semantics.H6: ('\n\n###### ', '\n\n'),
    Semantics.PARAGRAPH: ('\n\n', '')
}

# from https://enterprise.github.com/downloads/en/markdown-cheatsheet.pdf
special_chars = r"\`*_{}[]()#+-.!"
special_trans = str.maketrans(
    dict((char, f'\\{char}') for char in special_chars))


def escape(value: str) -> str:
    return value.translate(special_trans)


def style_markdown_tags(text: Child) -> Optional[Tuple[str, str]]:
    if isinstance(text, Semantic):
        try:
            return markdown_tags[text.semantic]
        except KeyError:
            pass
    elif isinstance(text, FontStyle) and text.font_style == FontStyles.ITALIC:
        return '*', '*'
    elif isinstance(text, FontWeight) and text.font_weight >= 550:
        return '**', '**'
    return None


@singledispatch
def render_markdown(text: BaseText) -> Iterable[str]:
    yield from map(escape, iter_strings(text))


@render_markdown.register(Child)
def _child(text: Child) -> Iterable[str]:
    tags = style_markdown_tags(text)
    if tags is not None:
        yield tags[0]
    yield from render_markdown(text.child)
    if tags is not None:
        yield tags[1]


@render_markdown.register(Join)
def _join(text: Join) -> Iterable[str]:
    for child in text.children:
        yield from render_markdown(child)
