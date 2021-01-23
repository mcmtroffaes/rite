from functools import singledispatch
from itertools import chain
from typing import Iterable, Dict, Optional, TypeVar

from TexSoup.data import TexText, TexCmd, BraceGroup, TexExpr

from rite.richtext import (
    BaseText, Rich, Join, Style, Semantics, FontSizes, FontStyles, FontVariants
)
from rite.richtext.utils import text_iter


semantics_map: Dict[Semantics, str] = {
    Semantics.STRONG: 'textbf',
    Semantics.EMPHASIS: 'emph',
    Semantics.SUBSCRIPT: 'textsubscript',
    Semantics.SUPERSCRIPT: 'textsuperscript',
    Semantics.CODE: 'texttt',
    Semantics.UNARTICULATED: 'underline',
    Semantics.STRIKETHROUGH: 'sout',
    Semantics.H1: 'chapter',
    Semantics.H2: 'section',
    Semantics.H3: 'subsection',
    Semantics.H4: 'subsubsection',
    Semantics.H5: 'paragraph',
    Semantics.H6: 'subparagraph',
}

font_size_map: Dict[FontSizes, str] = {
    FontSizes.XX_SMALL: 'scriptsize',
    FontSizes.X_SMALL: 'footnotesize',
    FontSizes.SMALL: 'small',
    FontSizes.LARGE: 'large',
    FontSizes.X_LARGE: 'Large',
    FontSizes.XX_LARGE: 'LARGE',
}

font_style_map: Dict[FontStyles, str] = {
    FontStyles.ITALIC: 'textit',
    FontStyles.OBLIQUE: 'textsl',
}

font_variant_map: Dict[FontVariants, str] = {
    FontVariants.SMALL_CAPS: 'textsc',
}

T = TypeVar('T')


def optional_iter(x: Optional[T]) -> Iterable[T]:
    if x is not None:
        yield x


def style_commands(style: Style) -> Iterable[str]:
    if style.semantics is not None:
        yield from optional_iter(semantics_map.get(style.semantics))
    yield from optional_iter(font_size_map.get(style.font_size))
    yield from optional_iter(font_style_map.get(style.font_style))
    yield from optional_iter(font_variant_map.get(style.font_variant))
    yield from optional_iter("textbf" if style.font_weight >= 550 else None)


@singledispatch
def render_latex(text: BaseText) -> Iterable[TexExpr]:
    for part in text_iter(text):
        yield TexText(part)


@render_latex.register(Rich)
def _rich(text: Rich) -> Iterable[TexExpr]:
    exprs: Iterable[TexExpr] = render_latex(text.child)
    for cmd in style_commands(text.style):
        exprs = [TexCmd(cmd, [BraceGroup(*exprs)])]
    yield from exprs


@render_latex.register(Join)
def _join(text: Join) -> Iterable[TexExpr]:
    return chain.from_iterable(map(render_latex, text.children))
