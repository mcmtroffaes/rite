from itertools import zip_longest
from typing import Iterable, List, Tuple, Optional, Dict
from xml.etree.ElementTree import Element

import TexSoup
import pytest

from rite.parse import ParseProtocol
from rite.parse.html import parse_html
from rite.parse.latex import parse_latex
from rite.parse.xml_etree import parse_xml_etree
from rite.render import RenderProtocol
from rite.render.html import render_html
from rite.render.latex import render_latex
from rite.render.markdown import render_markdown
from rite.render.plaintext import render_plaintext
from rite.render.rst import render_rst
from rite.render.xml_etree import render_xml_etree
from rite.richtext import (
    String, Join, BaseText, Style, Rich,
    Semantics, FontStyles, FontVariants, FontSizes
)
from common import _tt, _s, _st, _em, _b, _i


def test_protocol() -> None:
    # checks mypy recognizes our renderers as render protocols
    render_html_protocol: RenderProtocol[Iterable[str]] = render_html
    render_text_protocol: RenderProtocol[Iterable[str]] = render_plaintext
    render_markdown_protocol: RenderProtocol[Iterable[str]] = render_markdown
    render_rst_protocol: RenderProtocol[Iterable[str]] = render_rst
    parse_html_protocol: ParseProtocol[str] = parse_html
    s = _tt('xmas')
    assert ''.join(render_html_protocol(s)) == '<code>xmas</code>'
    assert ''.join(render_text_protocol(s)) == 'xmas'
    assert ''.join(render_markdown_protocol(s)) == '`xmas`'
    assert ''.join(render_rst_protocol(s)) == '``xmas``'
    assert list(parse_html_protocol('<code>xmas</code>')) == [s]


def test_protocol_class() -> None:
    class Render:
        def __call__(self, text: BaseText) -> int:
            return 123
    render_protocol: RenderProtocol[int] = Render()
    assert render_protocol(String('')) == 123


# should fail mypy
def test_protocol_bad_arg() -> None:
    def render(text: int) -> int:
        return 123
    render_protocol: RenderProtocol[float] = render  # type: ignore
    assert render_protocol(1) == 123  # type: ignore


# should fail mypy
def test_protocol_bad_rt() -> None:
    def render(text: BaseText) -> int:
        return 123
    render_protocol: RenderProtocol[str] = render  # type: ignore
    assert render_protocol(String('')) == 123  # type: ignore


def make_element(tag: str,
                 text: Optional[str] = None,
                 children: Optional[List[Element]] = None,
                 tail: Optional[str] = None,
                 attrib: Optional[Dict[str, str]] = None):
    element = Element(tag, attrib=attrib if attrib is not None else {})
    element.text = text
    if children is not None:
        element.extend(children)
    element.tail = tail
    return element


def none_to_empty(x: Optional[str]) -> str:
    if x is None:
        return ''
    else:
        return x


def assert_xml_etree_equal(
        x1: Tuple[Optional[str], Iterable[Element]],
        x2: Tuple[Optional[str], Iterable[Element]]) -> None:
    text1, e1s = x1
    text2, e2s = x2
    assert none_to_empty(text1) == none_to_empty(text2), 'head text mismatch'
    for e1, e2 in zip_longest(e1s, e2s, fillvalue=None):
        assert e1 is not None
        assert e2 is not None
        assert_elements_equal(e1, e2)


def assert_elements_equal(e1: Element, e2: Element) -> None:
    assert e1.tag == e2.tag, 'tag mismatch'
    assert none_to_empty(e1.text) == none_to_empty(e2.text), 'text mismatch'
    assert none_to_empty(e1.tail) == none_to_empty(e2.tail), 'tail mismatch'
    assert e1.attrib == e2.attrib, 'attrib mismatch'
    assert len(e1) == len(e2), 'children length mismatch'
    for c1, c2 in zip(e1, e2):
        assert_elements_equal(c1, c2)


@pytest.mark.parametrize(
    "texts,plaintext,html,markdown,rst,latex,latex_parsed,xml_etree", [
        (
                [_s('hello '), _em('brave'), _s(' world!')],
                'hello brave world!',
                'hello <em>brave</em> world!',
                r'hello *brave* world\!',
                r'hello *brave* world!',
                r'hello \emph{brave} world!',
                None,
                ('hello ', [
                    make_element('em', text='brave', tail=' world!')]),
        ),
        (
                [_s('hello '), _em('"<[*]>"'), _s(' world!')],
                'hello "<[*]>" world!',
                'hello <em>&quot;&lt;[*]&gt;&quot;</em> world!',
                r'hello *"<\[\*\]>"* world\!',
                r'hello *"<[\*]>"* world!',
                r'hello \emph{"<[*]>"} world!',
                None,
                ('hello ', [
                    make_element(
                        'em',
                        text='&quot;&lt;[*]&gt;&quot;', tail=' world!')]),
        ),
        (
                [
                    _s('hello '), _st('br'), _tt('a'), _s('v'), _em('e'),
                    _s(' world!'),
                ],
                'hello brave world!',
                'hello <strong>br</strong><code>a</code>v<em>e</em> world!',
                r'hello **br**`a`v*e* world\!',
                r'hello **br**``a``v*e* world!',
                r'hello \textbf{br}\texttt{a}v\emph{e} world!',
                Join([_s('hello '), _b('br'), _tt('a'), _s('v'), _em('e'),
                      _s(' world!')]),
                ('hello ', [
                    make_element('strong', text='br'),
                    make_element('code', text='a', tail='v'),
                    make_element('em', text='e', tail=' world!'),
                    ]),
        ),
        (
                [_st(Join([_s('h'), _em('e'), _s('l'), _tt('l'), _s('o')]))],
                'hello',
                '<strong>h<em>e</em>l<code>l</code>o</strong>',
                '**h*e*l`l`o**',
                '**h*e*l``l``o**',
                r'\textbf{h\emph{e}l\texttt{l}o}',
                _b(Join([_s('h'), _em('e'), _s('l'), _tt('l'), _s('o')])),
                (None, [
                    make_element('strong', text='h', children=[
                        make_element('em', text='e', tail='l'),
                        make_element('code', text='l', tail='o'),
                    ])])
        ),
        (
                [Rich(_s('hi'), Style(semantics=Semantics.MARK))],
                'hi',
                '<mark>hi</mark>',
                'hi',
                'hi',
                'hi',
                _s('hi'),
                (None, [make_element('mark', text='hi')]),
        ),
        (
                [Rich(_s('hi'), Style(font_weight=700))],
                'hi',
                '<b>hi</b>',
                '**hi**',
                '**hi**',
                r'\textbf{hi}',
                _b('hi'),
                (None, [make_element('b', text='hi')]),
        ),
        (
                [_i('hi')],
                'hi',
                '<i>hi</i>',
                '*hi*',
                '*hi*',
                r'\textit{hi}',
                None,
                (None, [make_element('i', text='hi')]),
        ),
        (
                [Rich(_s('hi'), Style(font_style=FontStyles.OBLIQUE))],
                'hi',
                '<span style="font-style:oblique">hi</span>',
                'hi',
                'hi',
                r'\textsl{hi}',
                None,
                (None, [make_element(
                    'span', text='hi',
                    attrib=dict(style="font-style:oblique"))]),
        ),
        (
                [Rich(_s('hi'), Style(font_weight=900))],
                'hi',
                '<span style="font-weight:900">hi</span>',
                '**hi**',
                '**hi**',
                r'\textbf{hi}',
                Rich(_s('hi'), Style(font_weight=700)),
                (None, [make_element('span', text='hi',
                                     attrib=dict(style='font-weight:900'))]),
        ),
        (
                [Rich(_s('hi'), Style(font_variant=FontVariants.SMALL_CAPS))],
                'hi',
                '<span style="font-variant:small-caps">hi</span>',
                'hi',
                'hi',
                r'\textsc{hi}',
                None,
                (None, [make_element(
                    'span', text='hi',
                    attrib=dict(style='font-variant:small-caps'))]),
        ),
        (
                [Rich(_s('hi'), Style(font_size=FontSizes.XX_LARGE))],
                'hi',
                '<span style="font-size:xx-large">hi</span>',
                'hi',
                'hi',
                r'\LARGE{hi}',
                None,
                (None, [make_element(
                    'span', text='hi',
                    attrib=dict(style='font-size:xx-large'))]),
        ),
        (
                [Rich(_s('hi'), Style(
                    semantics=Semantics.UNARTICULATED,
                    font_size=FontSizes.XX_LARGE,
                    font_style=FontStyles.OBLIQUE,
                    font_variant=FontVariants.SMALL_CAPS,
                    font_weight=300,
                ))],
                'hi',
                '<u style="font-size:xx-large;font-style:oblique;'
                'font-variant:small-caps;font-weight:300">hi</u>',
                'hi',
                'hi',
                r'\textsc{\textsl{\LARGE{\underline{hi}}}}',
                Rich(
                    Rich(
                        Rich(
                            Rich(
                                _s('hi'),
                                Style(semantics=Semantics.UNARTICULATED)),
                            Style(font_size=FontSizes.XX_LARGE)),
                        Style(font_style=FontStyles.OBLIQUE)),
                    Style(font_variant=FontVariants.SMALL_CAPS)),
                (None, [make_element(
                    'u', text='hi',
                    attrib=dict(
                        style='font-size:xx-large;font-style:oblique;'
                              'font-variant:small-caps;font-weight:300'))]),
        ),
    ])
def test_render_parse(
        texts: List[BaseText],
        plaintext: str, html: str, markdown: str, rst: str, latex: str,
        latex_parsed: Optional[BaseText],
        xml_etree: Tuple[Optional[str], Iterable[Element]]) -> None:
    assert ''.join(render_plaintext(Join(texts))) == plaintext
    assert ''.join(render_html(Join(texts))) == html
    assert ''.join(render_markdown(Join(texts))) == markdown
    assert ''.join(render_rst(Join(texts))) == rst
    assert ''.join(map(str, render_latex(Join(texts)))) == latex
    assert_xml_etree_equal(render_xml_etree(Join(texts)), xml_etree)
    assert list(parse_html(html)) == texts
    tex_env, _ = TexSoup.read(latex)
    assert parse_latex(tex_env) == (
           latex_parsed if latex_parsed is not None
           else (texts[0] if len(texts) == 1 else Join(texts)))


# some extra tests for coverage
@pytest.mark.parametrize(
    "texts,xml_etree", [
        ([String('he'), String('llo')], ('hello', [])),
        ([_em('he'), String('ll'), String('o')],
         (None, [make_element('em', text='he', tail='llo')])),
        ([_em('')],
         (None, [make_element('em', text='')])),
    ])
def test_render_xml_etree(
        texts: List[BaseText],
        xml_etree: Tuple[Optional[str], Iterable[Element]]) -> None:
    assert_xml_etree_equal(render_xml_etree(Join(texts)), xml_etree)


# some extra tests for coverage
@pytest.mark.parametrize(
    "element,texts", [
        (make_element('em', text=''), [_em('')]),
        (make_element('em'), [_em('')]),
    ])
def test_parse_xml_etree(element: Element, texts: List[BaseText]) -> None:
    assert list(parse_xml_etree(element)) == texts
