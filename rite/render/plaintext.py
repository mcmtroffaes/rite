from typing import Iterable

from rite.richtext import BaseText
from rite.richtext.utils import iter_strings


def render_plaintext(text: BaseText) -> Iterable[str]:
    return iter_strings(text)
