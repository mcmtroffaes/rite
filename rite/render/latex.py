from functools import singledispatch
from itertools import chain
from typing import Iterable, Dict, Optional, TypeVar

from pylatexenc.latexencode import unicode_to_latex

from rite.richtext import (
    Text, Semantics, FontSizes, FontStyles, FontVariants, Child,
    Semantic, FontSize, FontStyle, FontVariant, FontWeight, BaseText
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
    FontSizes.MEDIUM: 'normalsize',
    FontSizes.XX_SMALL: 'scriptsize',
    FontSizes.X_SMALL: 'footnotesize',
    FontSizes.SMALL: 'small',
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


def style_command(text: Child) -> Optional[str]:
    if isinstance(text, Semantic):
        return semantics_map.get(text.semantic)
    elif isinstance(text, FontStyle):
        return font_style_map.get(text.font_style)
    elif isinstance(text, FontVariant):
        return font_variant_map.get(text.font_variant)
    elif isinstance(text, FontWeight):
        return "textbf" if text.font_weight >= 550 else "textmd"
    return None


def style_macro(text: Child) -> Optional[str]:
    if isinstance(text, FontSize):
        return font_size_map.get(text.font_size)
    return None


@singledispatch
def _render_latex(text: Text) -> Iterable[str]:
    for part in text_iter(text):
        yield unicode_to_latex(part)


@_render_latex.register(BaseText)
def _base(text: BaseText) -> Iterable[str]:
    return chain.from_iterable(map(_render_latex, text))


@_render_latex.register(Child)
def _child(text: Child) -> Iterable[str]:
    cmd = style_command(text)
    mac = style_macro(text)
    if cmd is not None:
        yield from ["\\", cmd, "{"]
    elif mac is not None:
        yield from ["{", "\\", mac, " "]
    yield from _render_latex(text.child)
    if cmd is not None or mac is not None:
        yield "}"


class RenderLatex:
    def __call__(self, text: Text) -> Iterable[str]:
        return _render_latex(text)
