from rite.richtext import String
from rite.richtext.utils import list_join


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
