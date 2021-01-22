# some common helper functions for testing
from typing import Union, Callable

from rite.richtext import BaseText, String, Rich, Style, Semantics


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
    return Rich(child, Style(semantics=Semantics.STRONG))


@text_or_str
def _em(child: BaseText) -> BaseText:
    return Rich(child, Style(semantics=Semantics.EMPHASIS))


@text_or_str
def _tt(child: BaseText) -> BaseText:
    return Rich(child, Style(semantics=Semantics.CODE))
