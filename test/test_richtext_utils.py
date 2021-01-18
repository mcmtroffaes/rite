from typing import Callable, List, Dict

import pytest

from rite.richtext import String, Text, Tag, TagType, BaseText
from rite.richtext.utils import list_join, text_map, text_functor_map, text_raw, text_is_empty


@pytest.mark.parametrize(
    "text,func,result_map,result_functor_map,result_raw", [
        (
            Text([
                String("one "),
                Tag(TagType.STRONG, String("two")),
                String(" three"),
            ]),
            lambda x: "*" + x + "*",
            ['*one *', '*two*', '* three*'],
            Text([
                String("*one *"),
                Tag(TagType.STRONG, String("*two*")),
                String("* three*"),
            ]),
            'one two three',
        ),
])
def test_text_map(
        text: BaseText, func: Callable[[str], str],
        result_map: List[str], result_functor_map: BaseText,
        result_raw: str
):
    assert list(text_map(text, func)) == result_map
    assert text_functor_map(text, func) == result_functor_map
    assert text_raw(text) == result_raw


@pytest.mark.parametrize("text,is_empty", [
    (String(''), True),
    (String('hello'), False),
    (Tag(TagType.CODE, String('')), True),
    (Tag(TagType.CODE, String('hello')), False),
    (Text([]), True),
    (Text([String('')]), True),
    (Text([String(''), String('hello')]), False),
])
def test_text_is_empty(text: BaseText, is_empty: bool):
    assert text_is_empty(text) is is_empty


@pytest.mark.parametrize("inputs,outputs,kwargs", [
    ([], [], {}),
    (["one"], ["one"], {}),
    (["one", "two"], ["one", " and ", "two"], dict(sep2=" and ")),
    (
        ["one", "two", "three", "four"],
        ["one", ", ", "two", ", ", "three", ", ", "four"], {}
    ),
    (
        ["one", "two", "three", "four"],
        ["one", ", ", "two", ", ", "three", ", and ", "four"],
        dict(sep2=" and ", last_sep=", and ")
    ),
    (
        ["one", "two"],
        ["one", " and ", "two"],
        dict(sep2=" and ", other=" and others")
    ),
    (
        ["one", "two", "three", "four"],
        ["one", " and others"],
        dict(sep2=" and ", other=" and others")
    ),
])
def test_list_join(inputs: List[str], outputs: List[str], kwargs: Dict[str, str]):
    assert list_join(", ", inputs, **kwargs) == outputs
