# some common helper functions for testing
from typing import Union, Callable

from rite.richtext import (
    BaseText, String, Semantic, FontWeight, FontStyle, Semantics, FontStyles
)


def _s(value: str) -> BaseText:
    return String(value)


def text_or_str(f: Callable[[BaseText], BaseText]
                ) -> Callable[[Union[BaseText, str]], BaseText]:
    def _f(text: Union[BaseText, str]) -> BaseText:
        child = _s(text) if isinstance(text, str) else text
        return f(child)
    return _f


@text_or_str
def _st(child: BaseText) -> BaseText:
    return Semantic(child, Semantics.STRONG)


@text_or_str
def _em(child: BaseText) -> BaseText:
    return Semantic(child, Semantics.EMPHASIS)


@text_or_str
def _tt(child: BaseText) -> BaseText:
    return Semantic(child, Semantics.CODE)


@text_or_str
def _b(child: BaseText) -> BaseText:
    return FontWeight(child, 700)


@text_or_str
def _i(child: BaseText) -> BaseText:
    return FontStyle(child, FontStyles.ITALIC)
