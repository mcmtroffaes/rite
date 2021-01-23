# some common helper functions for testing

from rite.richtext import (
    Text, Semantic, FontWeight, FontStyle, Semantics, FontStyles
)


def _st(child: Text) -> Text:
    return Semantic(child, Semantics.STRONG)


def _em(child: Text) -> Text:
    return Semantic(child, Semantics.EMPHASIS)


def _tt(child: Text) -> Text:
    return Semantic(child, Semantics.CODE)


def _b(child: Text) -> Text:
    return FontWeight(child, 700)


def _i(child: Text) -> Text:
    return FontStyle(child, FontStyles.ITALIC)
