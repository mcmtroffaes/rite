from itertools import repeat

from rite.richtext import String, Tag, TagType, Join, Protected


def test_string():
    x = String('hello')
    assert list(x) == []
    assert x.fmap_iter(repeat(str.capitalize)) == String('Hello')


def test_join():
    x = Join([String('hello'), String(' '), String('world')])
    assert list(x) == [String('hello'), String(' '), String('world')]
    assert x.fmap_iter(repeat(str.capitalize)) \
           == Join([String('Hello'), String(' '), String('World')])


def test_tag():
    x = Tag(TagType.EMPHASIS, String('hello'))
    assert list(x) == [String('hello')]
    assert x.fmap_iter(repeat(str.capitalize)) \
           == Tag(TagType.EMPHASIS, String('Hello'))


def test_protected():
    x = Protected(String('hello'))
    assert list(x) == [String('hello')]
    assert x.fmap_iter(repeat(str.capitalize)) == x


# verify Text can contain String, Tag, and Text
def test_join_combined():
    x1 = Join([String('hello '),
               Tag(TagType.STRONG, String('brave')),
               Join([String(' world')])])
    x2 = Join([String('HELLO '),
               Tag(TagType.STRONG, String('BRAVE')),
               Join([String(' WORLD')])])
    assert x1.fmap_iter(repeat(str.upper)) == x2


# verify Tag can contain String, Tag, and Text
def test_tag_combined():
    s1 = String('hello')
    s2 = String('HELLO')
    x11 = Tag(TagType.EMPHASIS, s1)
    x21 = Tag(TagType.EMPHASIS, Tag(TagType.STRONG, s1))
    x12 = Tag(TagType.EMPHASIS, s2)
    x22 = Tag(TagType.EMPHASIS, Tag(TagType.STRONG, s2))
    assert x11.fmap_iter(repeat(str.upper)) == x12
    assert x21.fmap_iter(repeat(str.upper)) == x22
