import html

from functools import singledispatch
from typing import Iterable

from rite.richtext import BaseText, Tag, Join
from rite.richtext.utils import text_iter


def escape(value: str) -> str:
    return html.escape(value)


@singledispatch
def render_html(text: BaseText) -> Iterable[str]:
    yield from map(escape, text_iter(text))


@render_html.register(Tag)
def _tag(text: Tag) -> Iterable[str]:
    yield f"<{text.tag.value}>"
    yield from render_html(text.child)
    yield f"</{text.tag.value}>"


@render_html.register(Join)
def _join(text: Join) -> Iterable[str]:
    for child in text.children:
        yield from render_html(child)
