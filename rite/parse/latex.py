import unicodedata
from functools import singledispatch
from typing import Dict, Optional, Callable, Iterable, Tuple, List, Iterator

from pylatexenc.latexwalker import (
    LatexWalker, LatexNode, LatexCommentNode, LatexMacroNode, LatexGroupNode,
    LatexCharsNode, LatexSpecialsNode, LatexMathNode,
    get_default_latex_context_db
)
from pylatexenc.macrospec import MacroSpec, MacroStandardArgsParser, std_macro

from rite.richtext import (
    Text, Join,
    Semantics, FontSizes, FontStyles, FontVariants, Semantic,
    FontSize, FontStyle, FontWeight, FontVariant
)


def no_style() -> Callable[[Text], Text]:
    def func(child: Text) -> Text:
        return child
    return func


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
    'textmd': font_weight_style(400),
    'textbf': font_weight_style(700),
    'textup': text_up(),
    'textit': font_style_style(FontStyles.ITALIC),
    'textsl': font_style_style(FontStyles.OBLIQUE),
    'textsc': font_variant_style(FontVariants.SMALL_CAPS),
    'ensuremath': no_style(),
}

style_map_barren: Dict[str, Callable[[Text], Text]] = {
    'normalsize': font_size_style(FontSizes.MEDIUM),
    'scriptsize': font_size_style(FontSizes.XX_SMALL),
    'footnotesize': font_size_style(FontSizes.X_SMALL),
    'small': font_size_style(FontSizes.SMALL),
    'large': font_size_style(FontSizes.LARGE),
    'Large': font_size_style(FontSizes.X_LARGE),
    'LARGE': font_size_style(FontSizes.XX_LARGE),
}

marks_map: Dict[str, Tuple[str, str]] = {
    "`": ("\u0300", "`"),
    "'": ("\u0301", "´"),
    "^": ("\u0302", "^"),
    "~": ("\u0303", "˜"),
    "=": ("\u0304", "¯"),
    '.': ("\u0307", "˙"),
    '"': ("\u0308", "¨"),
    "H": ("\u030b", "˝"),
    "c": ("\u0327", "¸"),
    "k": ("\u0328", "˛"),
    "b": ("\u0331", "_"),
    "d": ("\u0323", "."),
    "r": ("\u030a", "˚"),
    "u": ("\u0306", "˘"),
    "v": ("\u030c", "ˇ"),
}


def _smart_join(texts: Iterable[Text]) -> Text:
    texts_list = list(texts)
    if not texts_list:
        return ''
    elif len(texts_list) == 1:
        return texts_list[0]
    else:
        return Join(texts_list)


def _parse_latex_nodes(nodes: Iterator[LatexNode]) -> Iterable[Text]:
    """Helper function to parse a list of nodes."""
    node: Optional[LatexNode] = next(nodes, None)
    while node is not None:
        if isinstance(node, LatexMacroNode) \
                and node.macroname in style_map_barren:
            yield style_map_barren[node.macroname](
                _smart_join(_parse_latex_nodes(nodes)))
        else:
            yield from _parse_latex(node)
        node = next(nodes, None)


def _text_macro_spec(name: str) -> MacroSpec:
    return MacroSpec(
        name, args_parser=MacroStandardArgsParser('{', args_math_mode=[False]))


def parse_latex(source: str) -> Iterable[Text]:
    context = get_default_latex_context_db()
    # add missing macros (will be fixed with pylatexenc > 2.8)
    context.add_context_category('rite', [
        _text_macro_spec('textmd'),
        _text_macro_spec('textup'),
        _text_macro_spec('textsf'),
        _text_macro_spec('texttt'),
        std_macro('underline', False, 1),
    ])
    nodes, _, _ = LatexWalker(source, latex_context=context).get_latex_nodes()
    yield from _parse_latex_nodes(iter(nodes))


@singledispatch
def _parse_latex(node: LatexNode) -> Iterable[Text]:
    raise TypeError(f'cannot handle latex node of type {type(node)}')


@_parse_latex.register(LatexCharsNode)
def _chars_node(node: LatexCharsNode) -> Iterable[Text]:
    yield node.chars


@_parse_latex.register(LatexSpecialsNode)
def _specials_node(node: LatexSpecialsNode) -> Iterable[Text]:
    yield node.specials_chars


@_parse_latex.register(LatexGroupNode)
def _group_node(node: LatexGroupNode) -> Iterable[Text]:
    yield from _parse_latex_nodes(iter(node.nodelist))


@_parse_latex.register(LatexCommentNode)
def _comment(node: LatexCommentNode) -> Iterable[Text]:
    return iter(())


def _single_chars_child(args: List[LatexNode]) -> Optional[str]:
    if len(args) == 1:
        arg: LatexNode = args[0]
        if isinstance(arg, LatexCharsNode):
            return arg.chars if len(arg.chars) == 1 else None
        elif isinstance(arg, LatexGroupNode):
            return _single_chars_child(arg.nodelist)
    return None


@_parse_latex.register(LatexMacroNode)
def _macro(node: LatexMacroNode) -> Iterable[Text]:

    style: Optional[Callable[[Text], Text]] = style_map.get(node.macroname)
    mark: Optional[Tuple[str, str]] = marks_map.get(node.macroname)
    char: Optional[str] = _single_chars_child(node.nodeargd.argnlist)
    if style is not None and len(node.nodeargd.argnlist) == 1:
        yield style(_smart_join(_parse_latex(node.nodeargd.argnlist[0])))
    elif mark is not None:
        if char is not None:
            yield unicodedata.normalize('NFC', char + mark[0])
        else:
            yield mark[1]
    else:
        return iter(())


@_parse_latex.register(LatexMathNode)
def _math(node: LatexMathNode) -> Iterable[Text]:
    for child_node in node.nodelist:
        yield from _parse_latex(child_node)
