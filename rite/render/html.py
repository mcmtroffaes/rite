import html

from functools import singledispatch
from typing import Iterable

from rite.render.xml_etree import style_properties
from rite.richtext import BaseText, Rich, Join
from rite.richtext.utils import text_iter


def escape(value: str) -> str:
    return html.escape(value)


@singledispatch
def render_html(text: BaseText) -> Iterable[str]:
    yield from map(escape, text_iter(text))


@render_html.register(Rich)
def _rich(text: Rich) -> Iterable[str]:
    tag, properties = style_properties(text.style)
    if properties:
        yield f'<{tag} style="{properties}">'
    else:
        yield f"<{tag}>"
    yield from render_html(text.child)
    yield f"</{tag}>"


@render_html.register(Join)
def _join(text: Join) -> Iterable[str]:
    for child in text.children:
        yield from render_html(child)
