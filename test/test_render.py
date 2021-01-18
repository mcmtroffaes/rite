from typing import Iterable

from rite.backends import RenderProtocol
from rite.backends.html import render_html
from rite.backends.markdown import render_markdown
from rite.backends.plaintext import render_plaintext
from rite.richtext import String, Tag, TagType, Text, BaseText


def test_protocol() -> None:
    # checks mypy recognizes our renderers as render protocols
    render_html_protocol: RenderProtocol[str] = render_html
    render_text_protocol: RenderProtocol[str] = render_plaintext
    render_markdown_protocol: RenderProtocol[str] = render_markdown
    s = Tag(TagType.CODE, String('xmas'))
    assert ''.join(render_html_protocol(s)) == '<code>xmas</code>'
    assert ''.join(render_text_protocol(s)) == 'xmas'
    assert ''.join(render_markdown_protocol(s)) == '`xmas`'


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


def test_hello_brave_world() -> None:
    s = Text([String('hello '),
              Tag(TagType.STRONG, String('brave')),
              String(' world!')])
    assert ''.join(render_plaintext(s)) == 'hello brave world!'
    assert ''.join(render_html(s)) == 'hello <strong>brave</strong> world!'
    assert ''.join(render_markdown(s)) == r'hello **brave** world\!'


def test_escape() -> None:
    s = Text([String('hello '),
              Tag(TagType.STRONG, String('"<[*]>"')),
              String(' world!')])
    assert ''.join(render_plaintext(s)) == 'hello "<[*]>" world!'
    assert ''.join(render_html(s)) == \
           'hello <strong>&quot;&lt;[*]&gt;&quot;</strong> world!'
    assert ''.join(render_markdown(s)) == r'hello **"<\[\*\]>"** world\!'
