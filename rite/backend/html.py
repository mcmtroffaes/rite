from functools import singledispatch
from typing import Iterable

from rite.richtext import BaseText, String, Tag, Text, text_map


@singledispatch
def render_html(text: BaseText) -> Iterable[str]:
    yield from text_map(lambda x: x)


@render_html.register(Tag)
def _tag(text: Tag) -> Iterable[str]:
    yield f"<{text.tag.value}>"
    yield from render_html(text.text)
    yield f"</{text.tag.value}>"


@render_html.register(Text)
def _text(text: Text) -> Iterable[str]:
    for part in text.parts:
        yield from render_html(part)
