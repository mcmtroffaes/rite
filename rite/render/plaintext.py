from typing import Iterable

from rite.richtext import BaseText


def render_plaintext(text: BaseText) -> Iterable[str]:
    yield from text
