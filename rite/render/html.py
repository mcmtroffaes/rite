import html

from functools import singledispatch
from typing import Iterable, Optional

from rite.richtext import BaseText, Rich, Join
from rite.richtext.utils import text_iter


def escape(value: str) -> str:
    return html.escape(value)


@singledispatch
def render_html(text: BaseText) -> Iterable[str]:
    yield from map(escape, text_iter(text))


@render_html.register(Rich)
def _rich(text: Rich) -> Iterable[str]:
    tag: Optional[str] = text.style.semantics.value \
        if text.style.semantics is not None else None
    if tag is not None:
        yield f"<{tag}>"
    yield from render_html(text.child)
    if tag is not None:
        yield f"</{tag}>"


@render_html.register(Join)
def _join(text: Join) -> Iterable[str]:
    for child in text.children:
        yield from render_html(child)
