from typing import Iterable

from rite.richtext import BaseText
from rite.richtext.utils import text_iter


def render_plaintext(text: BaseText) -> Iterable[str]:
    return text_iter(text)
