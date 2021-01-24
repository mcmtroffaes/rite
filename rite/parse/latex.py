import unicodedata
from functools import singledispatch
from typing import Dict, Optional, Callable, List

from TexSoup.data import TexCmd, TexExpr, TexEnv, TexText, BraceGroup
from TexSoup.utils import Token

from rite.richtext import (
    Text, Join,
    Semantics, FontSizes, FontStyles, FontVariants, Semantic,
    FontSize, FontStyle, FontWeight, FontVariant
)


def semantic_style(semantics: Semantics) -> Callable[[Text], Text]:
    def func(child: Text) -> Text:
        return Semantic(child, semantics)
    return func


def font_size_style(font_size: FontSizes) -> Callable[[Text], Text]:
    def func(child: Text) -> Text:
        return FontSize(child, font_size)
    return func


def font_style_style(font_style: FontStyles) -> Callable[[Text], Text]:
    def func(child: Text) -> Text:
        return FontStyle(child, font_style)
    return func


def font_variant_style(font_variant: FontVariants
                       ) -> Callable[[Text], Text]:
    def func(child: Text) -> Text:
        return FontVariant(child, font_variant)
    return func


def font_weight_style(font_weight: int) -> Callable[[Text], Text]:
    def func(child: Text) -> Text:
        return FontWeight(child, font_weight)
    return func


def text_up() -> Callable[[Text], Text]:
    def func(child: Text) -> Text:
        return FontVariant(
            FontStyle(child, FontStyles.NORMAL), FontVariants.NORMAL)
    return func


style_map: Dict[str, Callable[[Text], Text]] = {
    'emph': semantic_style(Semantics.EMPHASIS),
    'textsubscript': semantic_style(Semantics.SUBSCRIPT),
    'textsuperscript': semantic_style(Semantics.SUPERSCRIPT),
    'texttt': semantic_style(Semantics.CODE),
    'underline': semantic_style(Semantics.UNARTICULATED),
    'sout': semantic_style(Semantics.STRIKETHROUGH),
    'chapter': semantic_style(Semantics.H1),
    'section': semantic_style(Semantics.H2),
    'subsection': semantic_style(Semantics.H3),
    'subsubsection': semantic_style(Semantics.H4),
    'paragraph': semantic_style(Semantics.H5),
    'subparagraph': semantic_style(Semantics.H6),
    'normalsize': font_size_style(FontSizes.MEDIUM),
    'scriptsize': font_size_style(FontSizes.XX_SMALL),
    'footnotesize': font_size_style(FontSizes.X_SMALL),
    'small': font_size_style(FontSizes.SMALL),
    'large': font_size_style(FontSizes.LARGE),
    'Large': font_size_style(FontSizes.X_LARGE),
    'LARGE': font_size_style(FontSizes.XX_LARGE),
    'textmd': font_weight_style(400),
    'textbf': font_weight_style(700),
    'textup': text_up(),
    'textit': font_style_style(FontStyles.ITALIC),
    'textsl': font_style_style(FontStyles.OBLIQUE),
    'textsc': font_variant_style(FontVariants.SMALL_CAPS),
}


diacritical_marks: Dict[str, str] = {
    r"\`": "\u0300",
    r"\'": "\u0301",
    r"\^": "\u0302",
    r"\~": "\u0303",
    r"\=": "\u0304",
    r'\.': "\u0307",
    r'\"': "\u0308",
}


def _parse_contents(expr: TexExpr) -> Text:
    contents: List[TexExpr] = [item for item in expr.all]
    for i in range(len(contents) - 1):
        item1: TexExpr = contents[i]
        item2: TexExpr = contents[i + 1]
        mark = diacritical_marks.get(str(item1)) \
            if isinstance(item1, TexText) else None
        if mark is not None:
            if isinstance(item2, TexText) \
                    and len(item2) > 0 and item2[0].isalpha():
                contents[i] = TexText(unicodedata.normalize(
                    'NFC', item2[0] + mark))
                contents[i + 1] = TexText(item2[1:])
            if isinstance(item2, BraceGroup):
                item3: Optional[str] = item2.contents[0].text \
                    if len(item2.contents) == 1 \
                    and isinstance(item2.contents[0], Token) \
                    and len(item2.contents[0].text) == 1 \
                    else None
                if item3 is not None:
                    contents[i] = TexText('')
                    item2.contents = [Token(unicodedata.normalize(
                        'NFC', item3 + mark))]
    children: List[Text] = [parse_latex(child) for child in contents]
    if not children:
        return ''
    elif len(children) == 1:
        return children[0]
    elif all(isinstance(child, str) for child in children):
        return ''.join(child for child in children)  # type: ignore
    else:
        return Join(children)


@singledispatch
def parse_latex(expr: TexExpr) -> Text:
    return str(expr)


@parse_latex.register(TexEnv)
def _tex_env(expr: TexEnv) -> Text:
    return _parse_contents(expr)


@parse_latex.register(TexCmd)
def _tex_cmd(expr: TexCmd) -> Text:
    child: Text = _parse_contents(expr)
    style: Optional[Callable[[Text], Text]] = style_map.get(expr.name)
    if style is not None:
        return style(child)
    else:
        return child
