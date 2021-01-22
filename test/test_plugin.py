from typing import Iterable, Tuple, Optional
from xml.etree.ElementTree import Element

import pytest

from rite.parse import ParseProtocol
from rite.plugin import find_plugin
from rite.render import RenderProtocol
from rite.richtext import String, Rich, Style, Semantics

text = Rich(String('hi'), Style(semantics=Semantics.EMPHASIS))


def test_plugin_bad_group() -> None:
    with pytest.raises(ImportError):
        find_plugin('badgroup', 'html')


def test_plugin_bad_name() -> None:
    with pytest.raises(ImportError):
        find_plugin('rite.render', 'badname')


def test_plugin_render_html() -> None:
    render: RenderProtocol[Iterable[str]] \
        = find_plugin('rite.render', 'html')
    assert ''.join(render(text)) == '<em>hi</em>'


def test_plugin_render_markdown() -> None:
    render: RenderProtocol[Iterable[str]] \
        = find_plugin('rite.render', 'markdown')
    assert ''.join(render(text)) == '*hi*'


def test_plugin_render_plaintext() -> None:
    render: RenderProtocol[Iterable[str]] \
        = find_plugin('rite.render', 'plaintext')
    assert ''.join(render(text)) == 'hi'


def test_plugin_render_rst() -> None:
    render: RenderProtocol[Iterable[str]] \
        = find_plugin('rite.render', 'rst')
    assert ''.join(render(text)) == '*hi*'


def test_plugin_render_xml_etree() -> None:
    render: RenderProtocol[Tuple[Optional[str], Iterable[Element]]] \
        = find_plugin('rite.render', 'xml_etree')
    head, elements = render(text)
    elements = list(elements)
    assert not head
    assert len(elements) == 1
    assert elements[0].tag == 'em'
    assert elements[0].text == 'hi'


def test_plugin_parse_html() -> None:
    parse: ParseProtocol[str] = find_plugin('rite.parse', 'html')
    assert list(parse('<em>hi</em>')) == [text]


def test_plugin_parse_xml_etree() -> None:
    parse: ParseProtocol[Element] = find_plugin('rite.parse', 'xml_etree')
    element = Element('em')
    element.text = 'hi'
    assert list(parse(element)) == [text]
