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
    Text, Join, Semantics, FontStyles, FontVariants, FontSizes,
    Semantic, FontWeight, FontStyle, FontVariant, FontSize, Child
)
from common import _tt, _st, _em, _b, _i


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
        def __call__(self, text: Text) -> int:
            return 123
    render_protocol: RenderProtocol[int] = Render()
    assert render_protocol('') == 123


# should fail mypy
def test_protocol_bad_arg() -> None:
    def render(text: int) -> int:
        return 123
    render_protocol: RenderProtocol[float] = render  # type: ignore
    assert render_protocol(1) == 123  # type: ignore


# should fail mypy
def test_protocol_bad_rt() -> None:
    def render(text: Text) -> int:
        return 123
    render_protocol: RenderProtocol[str] = render  # type: ignore
    assert render_protocol('') == 123  # type: ignore


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
                ['hello ', _em('brave'), ' world!'],
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
                ['hello ', _em('"<[*]>"'), ' world!'],
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
                    'hello ', _st('br'), _tt('a'), 'v', _em('e'),
                    ' world!',
                ],
                'hello brave world!',
                'hello <strong>br</strong><code>a</code>v<em>e</em> world!',
                r'hello **br**`a`v*e* world\!',
                r'hello **br**``a``v*e* world!',
                r'hello \textbf{br}\texttt{a}v\emph{e} world!',
                Join(['hello ', _b('br'), _tt('a'), 'v', _em('e'),
                      ' world!']),
                ('hello ', [
                    make_element('strong', text='br'),
                    make_element('code', text='a', tail='v'),
                    make_element('em', text='e', tail=' world!'),
                    ]),
        ),
        (
                [_st(Join(['h', _em('e'), 'l', _tt('l'), 'o']))],
                'hello',
                '<strong>h<em>e</em>l<code>l</code>o</strong>',
                '**h*e*l`l`o**',
                '**h*e*l``l``o**',
                r'\textbf{h\emph{e}l\texttt{l}o}',
                _b(Join(['h', _em('e'), 'l', _tt('l'), 'o'])),
                (None, [
                    make_element('strong', text='h', children=[
                        make_element('em', text='e', tail='l'),
                        make_element('code', text='l', tail='o'),
                    ])])
        ),
        (
                [Semantic('hi', Semantics.MARK)],
                'hi',
                '<mark>hi</mark>',
                'hi',
                'hi',
                'hi',
                'hi',
                (None, [make_element('mark', text='hi')]),
        ),
        (
                [FontWeight('hi', 700)],
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
                [FontStyle('hi', FontStyles.OBLIQUE)],
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
                [FontWeight('hi', 900)],
                'hi',
                '<span style="font-weight:900">hi</span>',
                '**hi**',
                '**hi**',
                r'\textbf{hi}',
                FontWeight('hi', 700),
                (None, [make_element('span', text='hi',
                                     attrib=dict(style='font-weight:900'))]),
        ),
        (
                [FontVariant('hi', FontVariants.SMALL_CAPS)],
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
                [FontSize('hi', FontSizes.XX_LARGE)],
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
            [FontWeight(
                FontVariant(
                    FontStyle(
                        FontSize(
                            Semantic('hi', Semantics.UNARTICULATED),
                            FontSizes.XX_LARGE),
                        FontStyles.OBLIQUE),
                    FontVariants.SMALL_CAPS),
                300)],
            'hi',
            '<span style="font-weight:300">'
            '<span style="font-variant:small-caps">'
            '<span style="font-style:oblique">'
            '<span style="font-size:xx-large">'
            '<u>hi</u>'
            '</span></span></span></span>',
            'hi',
            'hi',
            r'\textmd{\textsc{\textsl{\LARGE{\underline{hi}}}}}',
            FontWeight(
                FontVariant(
                    FontStyle(
                        FontSize(
                            Semantic('hi', Semantics.UNARTICULATED),
                            FontSizes.XX_LARGE),
                        FontStyles.OBLIQUE),
                    FontVariants.SMALL_CAPS),
                400),
            (None, [make_element(
                'span', attrib=dict(style="font-weight:300"),
                children=[make_element(
                    'span', attrib=dict(style="font-variant:small-caps"),
                    children=[make_element(
                        'span', attrib=dict(style="font-style:oblique"),
                        children=[make_element(
                            'span', attrib=dict(style="font-size:xx-large"),
                            children=[make_element(
                                'u', text='hi'
                            )]
                        )]
                    )]
                )]
            )])
        ),
    ])
def test_render_parse(
        texts: List[Text],
        plaintext: str, html: str, markdown: str, rst: str, latex: str,
        latex_parsed: Optional[Text],
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
        (['he', 'llo'], ('hello', [])),
        ([_em('he'), 'll', 'o'],
         (None, [make_element('em', text='he', tail='llo')])),
        ([_em('')],
         (None, [make_element('em', text='')])),
    ])
def test_render_xml_etree(
        texts: List[Text],
        xml_etree: Tuple[Optional[str], Iterable[Element]]) -> None:
    assert_xml_etree_equal(render_xml_etree(Join(texts)), xml_etree)


# some extra tests for coverage
@pytest.mark.parametrize(
    "element,texts", [
        (make_element('em', text=''), [_em('')]),
        (make_element('em'), [_em('')]),
    ])
def test_parse_xml_etree(element: Element, texts: List[Text]) -> None:
    assert list(parse_xml_etree(element)) == texts


# some extra tests for coverage
def test_render_latex_new_text() -> None:
    class NewText(Child):
        pass

    assert ''.join(map(str, render_latex(NewText('hi')))) == 'hi'


# some extra tests for coverage
@pytest.mark.parametrize(
    "latex,text", [
        (r'\emph{}', _em('')),
        (r'{hi}', 'hi'),
        (r'\unknowncommnandxxx{hi}', 'hi'),
        (r'\unknowncommnandxxx{\emph{hi}}', _em('hi')),
        (r'{\emph{hi} how is {it going} \textit{today} sir}',
         Join([_em('hi'), ' how is ', 'it going', ' ', _i('today'), ' sir'])),
        (r"\'el\`eve", 'élève'),
    ])
def test_render_latex(latex: str, text: Text) -> None:
    tex_env, _ = TexSoup.read(latex)
    assert parse_latex(tex_env) == text
