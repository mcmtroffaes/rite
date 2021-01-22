from itertools import repeat

from rite.richtext import Join
from common import _em, _s, _st


def test_string():
    x = _s('hello')
    assert list(x) == []
    assert x.fmap_iter(repeat(str.capitalize)) == _s('Hello')


def test_join():
    x = Join([_s('hello'), _s(' '), _s('world')])
    assert list(x) == [_s('hello'), _s(' '), _s('world')]
    assert x.fmap_iter(repeat(str.capitalize)) \
           == Join([_s('Hello'), _s(' '), _s('World')])


def test_tag():
    x = _em('hello')
    assert list(x) == [_s('hello')]
    assert x.fmap_iter(repeat(str.capitalize)) == _em('Hello')


# verify Text can contain String, Tag, and Text
def test_join_combined():
    x1 = Join([_s('hello '), _st('brave'), Join([_s(' world')])])
    x2 = Join([_s('HELLO '), _st('BRAVE'), Join([_s(' WORLD')])])
    assert x1.fmap_iter(repeat(str.upper)) == x2


# verify Tag can contain String, Tag, and Text
def test_tag_combined():
    s1 = _s('hello')
    s2 = _s('HELLO')
    assert _em(s1).fmap_iter(repeat(str.upper)) == _em(s2)
    assert _em(_st(s1)).fmap_iter(repeat(str.upper)) == _em(_st(s2))
