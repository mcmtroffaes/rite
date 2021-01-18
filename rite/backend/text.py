from typing import Iterable

from rite.richtext import BaseText, text_map


def render_text(text: BaseText) -> Iterable[str]:
    yield from text_map(text, lambda x: x)
