from itertools import repeat

from rite.richtext import String, Tag, TagType, Text, Protected


def test_string():
    x = String('hello')
    assert list(map(str.capitalize, x)) == ['Hello']
    assert x.fmap_iter(repeat(str.capitalize)) == String('Hello')


def test_text():
    x = Text([String('hello'), String(' '), String('world')])
    assert list(map(str.capitalize, x)) \
           == ['Hello', ' ', 'World']
    assert x.fmap_iter(repeat(str.capitalize)) \
           == Text([String('Hello'), String(' '), String('World')])


def test_tag():
    x = Tag(TagType.EMPHASIS, String('hello'))
    assert list(map(str.capitalize, x)) \
           == ['Hello']
    assert x.fmap_iter(repeat(str.capitalize)) \
           == Tag(TagType.EMPHASIS, String('Hello'))


def test_protected():
    x = Protected(String('hello'))
    assert list(map(str.capitalize, x)) == ['Hello']
    assert x.fmap_iter(repeat(str.capitalize)) == x


# verify Text can contain String, Tag, and Text
def test_text_combined():
    x1 = Text([String('hello '),
               Tag(TagType.STRONG, String('brave')),
               Text([String(' world')])])
    x2 = Text([String('HELLO '),
               Tag(TagType.STRONG, String('BRAVE')),
               Text([String(' WORLD')])])
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
