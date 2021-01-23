import html

from functools import singledispatch
from typing import Iterable

from rite.render.xml_etree import text_style_property
from rite.richtext import Text, Child, Join, Semantic
from rite.richtext.utils import text_iter


def escape(value: str) -> str:
    return html.escape(value)


@singledispatch
def render_html(text: Text) -> Iterable[str]:
    yield from map(escape, text_iter(text))


@render_html.register(Child)
def _child(text: Child) -> Iterable[str]:
    tag = text.semantic.value if isinstance(text, Semantic) else "span"
    style_property = text_style_property(text)
    if style_property is not None:
        start = f'<{tag} style="{style_property}">'
        if start == '<span style="font-weight:700">':
            start = '<b>'
            tag = 'b'
        if start == '<span style="font-style:italic">':
            start = '<i>'
            tag = 'i'
        yield start
    else:
        yield f"<{tag}>"
    yield from render_html(text.child)
    yield f"</{tag}>"


@render_html.register(Join)
def _join(text: Join) -> Iterable[str]:
    for child in text.children:
        yield from render_html(child)
