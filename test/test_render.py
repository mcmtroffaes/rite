from typing import Iterable, List, Tuple, Optional
from xml.etree.ElementTree import Element

import pytest

from rite.parse import ParseProtocol
from rite.parse.html import parse_html
from rite.render import RenderProtocol
from rite.render.html import render_html
from rite.render.markdown import render_markdown
from rite.render.plaintext import render_plaintext
from rite.render.rst import render_rst
from rite.render.xml_etree import render_xml_etree
from rite.richtext import String, Tag, TagType, Join, BaseText


def test_protocol() -> None:
    # checks mypy recognizes our renderers as render protocols
    render_html_protocol: RenderProtocol[Iterable[str]] = render_html
    render_text_protocol: RenderProtocol[Iterable[str]] = render_plaintext
    render_markdown_protocol: RenderProtocol[Iterable[str]] = render_markdown
    render_rst_protocol: RenderProtocol[Iterable[str]] = render_rst
    parse_html_protocol: ParseProtocol[str] = parse_html
    s = Tag(TagType.CODE, String('xmas'))
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


def assert_xml_etree_equal(x1, x2):
    text1, e1s = x1
    text2, e2s = x2
    assert text1 == text2
    assert len(e1s) == len(e2s)
    for e1, e2 in zip(e1s, e2s):
        assert_elements_equal(e1, e2)


def assert_elements_equal(e1, e2):
    assert e1.tag == e2.tag
    assert e1.text == e2.text
    assert e1.tail == e2.tail
    assert e1.attrib == e2.attrib
    assert len(e1) == len(e2)
    for c1, c2 in zip(e1, e2):
        assert_elements_equal(c1, c2)


@pytest.mark.parametrize(
    "texts,plaintext,html,markdown,rst,xml_etree", [
        (
                [
                    String('hello '),
                    Tag(TagType.STRONG, String('brave')),
                    String(' world!'),
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
                    String('hello '),
                    Tag(TagType.STRONG, String('"<[*]>"')),
                    String(' world!'),
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
