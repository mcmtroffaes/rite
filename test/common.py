# some common helper functions for testing

from rite.richtext import (
    Text, BaseText, Semantic, FontWeight, FontStyle, Semantics, FontStyles
)


def _st(child: Text) -> BaseText:
    return Semantic(child, Semantics.STRONG)


def _em(child: Text) -> BaseText:
    return Semantic(child, Semantics.EMPHASIS)


def _tt(child: Text) -> BaseText:
    return Semantic(child, Semantics.CODE)


def _b(child: Text) -> BaseText:
    return FontWeight(child, 700)


def _i(child: Text) -> BaseText:
    return FontStyle(child, FontStyles.ITALIC)
