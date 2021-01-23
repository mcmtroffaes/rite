from itertools import repeat

from rite.richtext import Join
from common import _em, _st
from rite.richtext.utils import text_fmap_iter


def test_string() -> None:
    assert text_fmap_iter('hello', repeat(str.capitalize)) == 'Hello'


def test_join() -> None:
    x = Join(['hello', ' ', 'world'])
    assert list(x) == ['hello', ' ', 'world']
    assert text_fmap_iter(x, repeat(str.capitalize)) \
           == Join(['Hello', ' ', 'World'])


def test_rich() -> None:
    x = _em('hello')
    assert list(x) == ['hello']
    assert text_fmap_iter(x, repeat(str.capitalize)) == _em('Hello')


# verify Text can contain String, Tag, and Text
def test_join_combined() -> None:
    x1 = Join(['hello ', _st('brave'), Join([' world'])])
    x2 = Join(['HELLO ', _st('BRAVE'), Join([' WORLD'])])
    assert text_fmap_iter(x1, repeat(str.upper)) == x2


# verify Tag can contain String, Tag, and Text
def test_tag_combined() -> None:
    s1 = 'hello'
    s2 = 'HELLO'
    assert text_fmap_iter(_em(s1), repeat(str.upper)) == _em(s2)
    assert text_fmap_iter(_em(_st(s1)), repeat(str.upper)) == _em(_st(s2))
