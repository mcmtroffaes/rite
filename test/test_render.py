from typing import Iterable, Any

from rite.backend import RenderProtocol
from rite.backend.html import render_html
from rite.backend.markdown import render_markdown
from rite.backend.text import render_text
from rite.richtext import String, Tag, TagType, Text, BaseText


def test_protocol() -> None:
    # checks mypy recognizes our renderers as render protocols
    render_html_protocol: RenderProtocol[str] = render_html
    render_text_protocol: RenderProtocol[str] = render_text
    render_markdown_protocol: RenderProtocol[str] = render_markdown
    s = Tag(TagType.CODE, String('xmas'))
    assert ''.join(render_html_protocol(s)) == '<code>xmas</code>'
    assert ''.join(render_text_protocol(s)) == 'xmas'
    assert ''.join(render_markdown_protocol(s)) == '`xmas`'


def test_protocol_class() -> None:
    class Render:
        def __call__(self, text: BaseText) -> Iterable[int]:
            yield 123
    render_123_protocol: RenderProtocol[int] = Render()
    assert list(render_123_protocol(String(''))) == [123]


# should fail mypy
def test_protocol_bad_arg() -> Any:
    def render(text: int) -> Iterable[int]:
        yield 123
    render_protocol: RenderProtocol[float] = render  # type: ignore
    return render_protocol


# should fail mypy
def test_protocol_bad_rt() -> Any:
    def render(text: BaseText) -> Iterable[int]:
        yield 123
    render_protocol: RenderProtocol[str] = render  # type: ignore
    return render_protocol


def test_hello_brave_world() -> None:
    s = Text([String('hello '),
              Tag(TagType.STRONG, String('brave')),
              String(' world!')])
    assert ''.join(render_text(s)) == 'hello brave world!'
    assert ''.join(render_html(s)) == 'hello <strong>brave</strong> world!'
    assert ''.join(render_markdown(s)) == r'hello **brave** world\!'
