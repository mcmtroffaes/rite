from itertools import repeat

from rite.richtext import String, Tag, TagType, Text
from rite.richtext.utils import list_join


def test_string():
    x = String('hello')
    assert list(x.map_iter(repeat(str.capitalize))) == ['Hello']
    assert x.functor_map_iter(repeat(str.capitalize)) == String('Hello')


def test_text():
    x = Text([String('hello'), String(' '), String('world')])
    assert list(x.map_iter(repeat(str.capitalize))) \
           == ['Hello', ' ', 'World']
    assert x.functor_map_iter(repeat(str.capitalize)) \
           == Text([String('Hello'), String(' '), String('World')])


def test_tag():
    x = Tag(TagType.EMPHASIZE, String('hello'))
    assert list(x.map_iter(repeat(str.capitalize))) \
           == ['Hello']
    assert x.functor_map_iter(repeat(str.capitalize)) \
           == Tag(TagType.EMPHASIZE, String('Hello'))


# verify Text can contain String, Tag, and Text
def test_text_combined():
    x1 = Text([String('hello '),
               Tag(TagType.STRONG, String('brave')),
               Text([String(' world')])])
    x2 = Text([String('HELLO '),
               Tag(TagType.STRONG, String('BRAVE')),
               Text([String(' WORLD')])])
    assert x1.functor_map_iter(repeat(str.upper)) == x2


# verify Tag can contain String, Tag, and Text
def test_tag_combined():
    s1 = String('hello')
    s2 = String('HELLO')
    x11 = Tag(TagType.EMPHASIZE, s1)
    x21 = Tag(TagType.EMPHASIZE, Tag(TagType.STRONG, s1))
    x12 = Tag(TagType.EMPHASIZE, s2)
    x22 = Tag(TagType.EMPHASIZE, Tag(TagType.STRONG, s2))
    assert x11.functor_map_iter(repeat(str.upper)) == x12
    assert x21.functor_map_iter(repeat(str.upper)) == x22


def test_list_join():
    x1 = String("one")
    x2 = String("two")
    x3 = String("three")
    x4 = String("four")
    xs = [x1, x2, x3, x4]
    sep = String(", ")
    sep2 = String(" and ")
    last_sep = String(", and ")
    other = String(" and others")
    assert list_join(sep, []) == []
    assert list_join(sep, [x1]) == [x1]
    assert list_join(sep, xs[:2], sep2=sep2, last_sep=last_sep) == [
        String("one"),
        String(" and "),
        String("two"),
    ]
    assert list_join(sep, xs) == [
        String("one"),
        String(", "),
        String("two"),
        String(", "),
        String("three"),
        String(", "),
        String("four"),
    ]
    assert list_join(sep, xs, sep2=sep2, last_sep=last_sep) == [
        String("one"),
        String(", "),
        String("two"),
        String(", "),
        String("three"),
        String(", and "),
        String("four"),
    ]
    assert list_join(sep, xs[:2], sep2=sep2, other=other) == [
        String("one"),
        String(" and "),
        String("two"),
    ]
    assert list_join(sep, xs, sep2=sep2, other=other) == [
        String("one"),
        String(" and others"),
    ]
