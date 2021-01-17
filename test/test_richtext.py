from rite.richtext import String, Tag, TagType, Text, join_text, _join_list


def test_string():
    x = String('hello')
    assert x.apply(str.capitalize) == String('Hello')
    assert x.apply_start(str.capitalize) == String('Hello')
    assert x.apply_end(str.capitalize) == String('Hello')


def test_text():
    x = Text([String('hello'), String(' '), String('world')])
    assert x.apply(str.capitalize) \
           == Text([String('Hello'), String(' '), String('World')])
    assert x.apply_start(str.capitalize) \
           == Text([String('Hello'), String(' '), String('world')])
    assert x.apply_end(str.capitalize) \
           == Text([String('hello'), String(' '), String('World')])


def test_tag():
    x = Tag(TagType.EMPHASIZE, String('hello'))
    assert x.apply(str.capitalize) \
           == Tag(TagType.EMPHASIZE, String('Hello'))
    assert x.apply_start(str.capitalize) \
           == Tag(TagType.EMPHASIZE, String('Hello'))
    assert x.apply_end(str.capitalize) \
           == Tag(TagType.EMPHASIZE, String('Hello'))


# verify Text can contain String, Tag, and Text
def test_text_combined():
    x1 = Text([String('hello '),
               Tag(TagType.STRONG, String('brave')),
               Text([String(' world')])])
    x2 = Text([String('HELLO '),
               Tag(TagType.STRONG, String('BRAVE')),
               Text([String(' WORLD')])])
    x3 = Text([String('HELLO '),
               Tag(TagType.STRONG, String('brave')),
               Text([String(' world')])])
    x4 = Text([String('hello '),
               Tag(TagType.STRONG, String('brave')),
               Text([String(' WORLD')])])
    assert x1.apply(str.upper) == x2
    assert x1.apply_start(str.upper) == x3
    assert x1.apply_end(str.upper) == x4


# verify Tag can contain String, Tag, and Text
def test_tag_combined():
    s1 = String('hello')
    s2 = String('HELLO')
    x11 = Tag(TagType.EMPHASIZE, s1)
    x21 = Tag(TagType.EMPHASIZE, Tag(TagType.STRONG, s1))
    x31 = Tag(TagType.EMPHASIZE, Text([s1]))
    x12 = Tag(TagType.EMPHASIZE, s2)
    x22 = Tag(TagType.EMPHASIZE, Tag(TagType.STRONG, s2))
    x32 = Tag(TagType.EMPHASIZE, Text([s2]))
    assert x11.apply(str.upper) == x12
    assert x21.apply_start(str.upper) == x22
    assert x31.apply_end(str.upper) == x32


def test_join_list():
    assert list(_join_list([], 0)) == []
    assert list(_join_list([1], 0)) == [1]
    assert list(_join_list([1, 2], 0)) == [1, 0, 2]
    assert list(_join_list([1, 2, 3], 0)) == [1, 0, 2, 0, 3]
    assert list(_join_list([1, 2, 3, 4], 0)) == [1, 0, 2, 0, 3, 0, 4]


def test_join_text():
    x1 = String("one")
    x2 = String("two")
    x3 = String("three")
    x4 = String("four")
    xs = [x1, x2, x3, x4]
    sep = String(", ")
    sep2 = String(" and ")
    last_sep = String(", and ")
    other = String(" and others")
    assert join_text(xs, sep=sep) == Text([
        String("one"),
        String(", "),
        String("two"),
        String(", "),
        String("three"),
        String(", "),
        String("four"),
    ])
    assert join_text(xs[:2], sep=sep, sep2=sep2, last_sep=last_sep) == Text([
        String("one"),
        String(" and "),
        String("two"),
    ])
    assert join_text(xs, sep=sep, sep2=sep2, last_sep=last_sep) == Text([
        String("one"),
        String(", "),
        String("two"),
        String(", "),
        String("three"),
        String(", and "),
        String("four"),
    ])
    assert join_text(xs, other=other) == Text([
        String("one"),
        String(" and others"),
    ])
