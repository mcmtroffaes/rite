from itertools import zip_longest
from typing import Iterable, List, Tuple, Optional
from xml.etree.ElementTree import Element

import pytest

from rite.parse import ParseProtocol
from rite.parse.html import parse_html
from rite.parse.xml_etree import parse_xml_etree
from rite.render import RenderProtocol
from rite.render.html import render_html
from rite.render.markdown import render_markdown
from rite.render.plaintext import render_plaintext
from rite.render.rst import render_rst
from rite.render.xml_etree import render_xml_etree
from rite.richtext import String, Join, BaseText
from common import _tt, _s, _st, _em


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
                 tail: Optional[str] = None):
    element = Element(tag)
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
    "texts,plaintext,html,markdown,rst,xml_etree", [
        (
                [
                    _s('hello '),
                    _st('brave'),
                    _s(' world!'),
                ],
                'hello brave world!',
                'hello <strong>brave</strong> world!',
                r'hello **brave** world\!',
                r'hello **brave** world!',
                ('hello ', [
                    make_element('strong', text='brave', tail=' world!')]),
        ),
        (
                [
                    _s('hello '),
                    _st('"<[*]>"'),
                    _s(' world!'),
                ],
                'hello "<[*]>" world!',
                'hello <strong>&quot;&lt;[*]&gt;&quot;</strong> world!',
                r'hello **"<\[\*\]>"** world\!',
                r'hello **"<[\*]>"** world!',
                ('hello ', [
                    make_element(
                        'strong',
                        text='&quot;&lt;[*]&gt;&quot;', tail=' world!')]),
        ),
        (
                [
                    _s('hello '),
                    _st('br'),
                    _tt('a'),
                    _s('v'),
                    _em('e'),
                    _s(' world!'),
                ],
                'hello brave world!',
                'hello <strong>br</strong><code>a</code>v<em>e</em> world!',
                r'hello **br**`a`v*e* world\!',
                r'hello **br**``a``v*e* world!',
                ('hello ', [
                    make_element('strong', text='br'),
                    make_element('code', text='a', tail='v'),
                    make_element('em', text='e', tail=' world!'),
                    ]),
        ),
        (
                [
                    _st(Join([
                        _s('h'),
                        _em('e'),
                        _s('l'),
                        _tt('l'),
                        _s('o'),
                    ])),
                ],
                'hello',
                '<strong>h<em>e</em>l<code>l</code>o</strong>',
                '**h*e*l`l`o**',
                '**h*e*l``l``o**',
                (None, [
                    make_element('strong', text='h', children=[
                        make_element('em', text='e', tail='l'),
                        make_element('code', text='l', tail='o'),
                    ])])
        ),
    ])
def test_render_parse(
        texts: List[BaseText],
        plaintext: str, html: str, markdown: str, rst: str,
        xml_etree: Tuple[Optional[str], Iterable[Element]]) -> None:
    assert ''.join(render_plaintext(Join(texts))) == plaintext
    assert ''.join(render_html(Join(texts))) == html
    assert ''.join(render_markdown(Join(texts))) == markdown
    assert ''.join(render_rst(Join(texts))) == rst
    assert_xml_etree_equal(render_xml_etree(Join(texts)), xml_etree)
    assert list(parse_html(html)) == texts


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
