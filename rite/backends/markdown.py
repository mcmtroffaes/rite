from functools import singledispatch
from typing import Iterable, Dict, Tuple

from rite.richtext import BaseText, Text, Tag, TagType
from rite.richtext.utils import text_map

markdown_tags: Dict[TagType, Tuple[str, str]] = {
    TagType.EMPHASIZE: ('*', '*'),
    TagType.STRONG: ('**', '**'),
    TagType.CODE: ('`', '`'),
    TagType.SUBSCRIPT: ('<sub>', '</sub>'),
    TagType.SUPERSCRIPT: ('<sup>', '</sup>'),
}

# from https://enterprise.github.com/downloads/en/markdown-cheatsheet.pdf
special_chars = r"\`*_{}[]()#+-.!"
special_trans = str.maketrans(
    dict((char, f'\\{char}') for char in special_chars))


def escape(value: str) -> str:
    return value.translate(special_trans)


@singledispatch
def render_markdown(text: BaseText) -> Iterable[str]:
    yield from text_map(text, escape)


@render_markdown.register(Tag)
def _tag(text: Tag) -> Iterable[str]:
    tags = markdown_tags[text.tag]
    yield tags[0]
    yield from render_markdown(text.text)
    yield tags[1]


@render_markdown.register(Text)
def _text(text: Text) -> Iterable[str]:
    for part in text.parts:
        yield from render_markdown(part)
