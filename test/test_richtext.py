from rite.richtext import String, Tag, TagType, Text


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
