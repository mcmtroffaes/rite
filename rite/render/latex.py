from functools import singledispatch
from itertools import chain
from typing import Iterable, Dict, Optional, TypeVar

from TexSoup.data import TexText, TexCmd, BraceGroup, TexExpr

from rite.richtext import (
    Text, Join, Semantics, FontSizes, FontStyles, FontVariants, Child,
    Semantic, FontSize, FontStyle, FontVariant, FontWeight
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
    FontSizes.MEDIUM: 'normalsize',
    FontSizes.LARGE: 'large',
    FontSizes.X_LARGE: 'Large',
    FontSizes.XX_LARGE: 'LARGE',
}

# see https://tex.stackexchange.com/a/5012
font_style_map: Dict[FontStyles, str] = {
    FontStyles.NORMAL: 'textup',
    FontStyles.ITALIC: 'textit',
    FontStyles.OBLIQUE: 'textsl',
}

# see https://tex.stackexchange.com/a/5012
font_variant_map: Dict[FontVariants, str] = {
    FontVariants.NORMAL: 'textup',
    FontVariants.SMALL_CAPS: 'textsc',
}

T = TypeVar('T')


def optional_iter(x: Optional[T]) -> Iterable[T]:
    if x is not None:
        yield x


def style_command(text: Child) -> Optional[str]:
    if isinstance(text, Semantic):
        return semantics_map.get(text.semantic)
    elif isinstance(text, FontSize):
        return font_size_map.get(text.font_size)
    elif isinstance(text, FontStyle):
        return font_style_map.get(text.font_style)
    elif isinstance(text, FontVariant):
        return font_variant_map.get(text.font_variant)
    elif isinstance(text, FontWeight):
        return "textbf" if text.font_weight >= 550 else "textmd"
    return None


@singledispatch
def render_latex(text: Text) -> Iterable[TexExpr]:
    for part in text_iter(text):
        yield TexText(part)


@render_latex.register(Child)
def _child(text: Child) -> Iterable[TexExpr]:
    exprs: Iterable[TexExpr] = render_latex(text.child)
    cmd = style_command(text)
    if cmd is not None:
        exprs = [TexCmd(cmd, [BraceGroup(*exprs)])]
    yield from exprs


@render_latex.register(Join)
def _join(text: Join) -> Iterable[TexExpr]:
    return chain.from_iterable(map(render_latex, text.children))
