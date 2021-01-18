from typing import Iterable

from rite.richtext import BaseText
from rite.richtext.utils import text_strings


def render_text(text: BaseText) -> Iterable[str]:
    yield from text_strings(text)
