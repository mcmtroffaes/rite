from functools import singledispatch
from typing import Iterable

from rite.richtext import BaseText, String, Tag, Text


@singledispatch
def render_text(text: BaseText) -> Iterable[str]:
    raise TypeError(f'rendering {type(text)} to text is not implemented')


@render_text.register(String)
def _string(text: String) -> Iterable[str]:
    yield f"{text.value}"


@render_text.register(Tag)
def _tag(text: Tag) -> Iterable[str]:
    yield from render_text(text.text)


@render_text.register(Text)
def _text(text: Text) -> Iterable[str]:
    for part in text.parts:
        yield from render_text(part)
