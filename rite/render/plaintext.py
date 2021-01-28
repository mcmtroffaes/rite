from typing import Iterable

from rite.richtext import Text
from rite.richtext.utils import text_iter


class RenderPlaintext:
    def __call__(self, text: Text) -> Iterable[str]:
        return text_iter(text)
