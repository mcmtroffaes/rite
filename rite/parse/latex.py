from functools import singledispatch
from typing import Dict, Optional

from TexSoup.data import TexCmd, BraceGroup, TexExpr, TexEnv

from rite.richtext import (
    BaseText, String, Rich, Join,
    Style, Semantics, FontSizes, FontStyles, FontVariants
)


style_map: Dict[str, Style] = {
    'emph': Style(Semantics.EMPHASIS),
    'textsubscript': Style(Semantics.SUBSCRIPT),
    'textsuperscript': Style(Semantics.SUPERSCRIPT),
    'texttt': Style(Semantics.CODE),
    'underline': Style(Semantics.UNARTICULATED),
    'sout': Style(Semantics.STRIKETHROUGH),
    'chapter': Style(Semantics.H1),
    'section': Style(Semantics.H2),
    'subsection': Style(Semantics.H3),
    'subsubsection': Style(Semantics.H4),
    'paragraph': Style(Semantics.H5),
    'subparagraph': Style(Semantics.H6),
    'scriptsize': Style(font_size=FontSizes.XX_SMALL),
    'footnotesize': Style(font_size=FontSizes.X_SMALL),
    'small': Style(font_size=FontSizes.SMALL),
    'large': Style(font_size=FontSizes.LARGE),
    'Large': Style(font_size=FontSizes.X_LARGE),
    'LARGE': Style(font_size=FontSizes.XX_LARGE),
    'textbf': Style(font_weight=700),
    'textit': Style(font_style=FontStyles.ITALIC),
    'textsl': Style(font_style=FontStyles.OBLIQUE),
    'textsc': Style(font_variant=FontVariants.SMALL_CAPS),
}


def _parse_contents(expr: TexExpr) -> BaseText:
    children = [parse_latex(child) for child in expr.contents]
    if not children:
        return String('')
    elif len(children) == 1:
        return children[0]
    elif all(isinstance(child, String) for child in children):
        return String(''.join(
            child.value for child in children))  # type: ignore
    else:
        return Join(children)


@singledispatch
def parse_latex(expr: TexExpr) -> BaseText:
    return String(str(expr))


@parse_latex.register(TexEnv)
def _tex_env(expr: TexEnv) -> BaseText:
    return _parse_contents(expr)


@parse_latex.register(TexCmd)
def _tex_cmd(expr: TexCmd) -> BaseText:
    child: BaseText = _parse_contents(expr)
    style: Optional[Style] = style_map.get(expr.name)
    if style is not None:
        return Rich(child, style)
    else:
        return child


@parse_latex.register(BraceGroup)
def _brace_group(expr: BraceGroup) -> BaseText:
    return _parse_contents(expr)
