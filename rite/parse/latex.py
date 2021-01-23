from functools import singledispatch
from typing import Dict, Optional, Callable, List

from TexSoup.data import TexCmd, BraceGroup, TexExpr, TexEnv

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
    'scriptsize': font_size_style(FontSizes.XX_SMALL),
    'footnotesize': font_size_style(FontSizes.X_SMALL),
    'small': font_size_style(FontSizes.SMALL),
    'large': font_size_style(FontSizes.LARGE),
    'Large': font_size_style(FontSizes.X_LARGE),
    'LARGE': font_size_style(FontSizes.XX_LARGE),
    'textmd': font_weight_style(400),
    'textbf': font_weight_style(700),
    'textit': font_style_style(FontStyles.ITALIC),
    'textsl': font_style_style(FontStyles.OBLIQUE),
    'textsc': font_variant_style(FontVariants.SMALL_CAPS),
}


def _parse_contents(expr: TexExpr) -> Text:
    children: List[Text] = [parse_latex(child) for child in expr.all]
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
