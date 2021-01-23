from itertools import repeat

from rite.richtext import Join
from common import _em, _s, _st
from rite.richtext.utils import text_fmap_iter


def test_string() -> None:
    assert text_fmap_iter('hello', repeat(str.capitalize)) == 'Hello'


def test_join() -> None:
    x = Join([_s('hello'), _s(' '), _s('world')])
    assert list(x) == [_s('hello'), _s(' '), _s('world')]
    assert text_fmap_iter(x, repeat(str.capitalize)) \
           == Join([_s('Hello'), _s(' '), _s('World')])


def test_rich() -> None:
    x = _em('hello')
    assert list(x) == [_s('hello')]
    assert text_fmap_iter(x, repeat(str.capitalize)) == _em('Hello')


# verify Text can contain String, Tag, and Text
def test_join_combined() -> None:
    x1 = Join([_s('hello '), _st('brave'), Join([_s(' world')])])
    x2 = Join([_s('HELLO '), _st('BRAVE'), Join([_s(' WORLD')])])
    assert text_fmap_iter(x1, repeat(str.upper)) == x2


# verify Tag can contain String, Tag, and Text
def test_tag_combined() -> None:
    s1 = _s('hello')
    s2 = _s('HELLO')
    assert text_fmap_iter(_em(s1), repeat(str.upper)) == _em(s2)
    assert text_fmap_iter(_em(_st(s1)), repeat(str.upper)) == _em(_st(s2))
