from typing import Iterable

from rite.richtext import BaseText
from rite.richtext.utils import text_map


def render_text(text: BaseText) -> Iterable[str]:
    yield from text_map(text, lambda x: x)
