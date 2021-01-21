from typing import Iterable, List

import pytest

from rite.parse import ParseProtocol
from rite.parse.html import parse_html
from rite.render import RenderProtocol
from rite.render.html import render_html
from rite.render.markdown import render_markdown
from rite.render.plaintext import render_plaintext
from rite.render.rst import render_rst
from rite.richtext import String, Tag, TagType, Join, BaseText


def test_protocol() -> None:
    # checks mypy recognizes our renderers as render protocols
    render_html_protocol: RenderProtocol[str] = render_html
    render_text_protocol: RenderProtocol[str] = render_plaintext
    render_markdown_protocol: RenderProtocol[str] = render_markdown
    render_rst_protocol: RenderProtocol[str] = render_rst
    parse_html_protocol: ParseProtocol[str] = parse_html
    s = Tag(TagType.CODE, String('xmas'))
    assert ''.join(render_html_protocol(s)) == '<code>xmas</code>'
    assert ''.join(render_text_protocol(s)) == 'xmas'
    assert ''.join(render_markdown_protocol(s)) == '`xmas`'
    assert ''.join(render_rst_protocol(s)) == '``xmas``'
    assert list(parse_html_protocol('<code>xmas</code>')) == [s]


def test_protocol_class() -> None:
    class Render:
        def __call__(self, text: BaseText) -> Iterable[int]:
            yield 123
    render_protocol: RenderProtocol[int] = Render()
    assert list(render_protocol(String(''))) == [123]


# should fail mypy
def test_protocol_bad_arg() -> None:
    def render(text: int) -> Iterable[int]:
        yield 123
    render_protocol: RenderProtocol[float] = render  # type: ignore
    assert list(render_protocol(1)) == [123]  # type: ignore


# should fail mypy
def test_protocol_bad_rt() -> None:
    def render(text: BaseText) -> Iterable[int]:
        yield 123
    render_protocol: RenderProtocol[str] = render  # type: ignore
    assert list(render_protocol(String(''))) == [123]  # type: ignore


@pytest.mark.parametrize(
    "texts,plaintext,html,markdown,rst", [
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
        ),
    ])
def test_render_parse(
        texts: List[BaseText],
        plaintext: str, html: str, markdown: str, rst: str) -> None:
    assert ''.join(render_plaintext(Join(texts))) == plaintext
    assert ''.join(render_html(Join(texts))) == html
    assert ''.join(render_markdown(Join(texts))) == markdown
    assert ''.join(render_rst(Join(texts))) == rst
    assert list(parse_html(html)) == texts
