from typing import Iterable

from rite.richtext import Text
from rite.richtext.utils import text_iter


def render_plaintext(text: Text) -> Iterable[str]:
    return text_iter(text)
