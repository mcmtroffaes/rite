from typing import Callable, List, Dict

import pytest

from rite.richtext import String, Text, Tag, TagType, BaseText
from rite.richtext.utils import (
    list_join, text_map, text_functor_map, text_raw, text_is_empty,
    text_is_lower, text_is_upper, text_lower, text_upper,
    text_capitalize, text_capfirst,
)


# helper function for constructing test cases
def _s(value: str) -> String:
    return String(value)


# helper function for constructing test cases
def _t(value: str) -> Tag:
    return Tag(TagType.CODE, String(value))


@pytest.mark.parametrize(
    "text,func,result_map,result_functor_map,result_raw", [
        (
            Text([_s("one "), _t("two"), _s(" three")]),
            lambda x: "*" + x + "*",
            ['*one *', '*two*', '* three*'],
            Text([_s("*one *"), _t("*two*"), _s("* three*")]),
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
    (_s(''), True),
    (_s('hello'), False),
    (_t(''), True),
    (_t('hello'), False),
    (Text([]), True),
    (Text([_s('')]), True),
    (Text([_s(''), _s('hello')]), False),
])
def test_text_is_empty(text: BaseText, is_empty: bool):
    assert text_is_empty(text) is is_empty


@pytest.mark.parametrize("text,is_lower,is_upper", [
    (_s('hello'), True, False),
    (_s('HELLO'), False, True),
    (_s('heLLO'), False, False),
    (_t('hello'), True, False),
    (_t('HELLO'), False, True),
    (_t('heLLO'), False, False),
    (Text([_s('hello'), _s(' world')]), True, False),
    (Text([_s('HELLO'), _s(' WORLD')]), False, True),
    (Text([_s('hello'), _s(' WORLD')]), False, False),
])
def test_text_is_lower_upper(text: BaseText, is_lower: bool, is_upper: bool):
    assert text_is_lower(text) is is_lower
    assert text_is_upper(text) is is_upper


@pytest.mark.parametrize("text,lower,upper", [
    (_s('hello'), _s('hello'), _s('HELLO')),
    (_s('HELLO'), _s('hello'), _s('HELLO')),
    (_s('heLLO'), _s('hello'), _s('HELLO')),
    (_t('hello'), _t('hello'), _t('HELLO')),
    (_t('HELLO'), _t('hello'), _t('HELLO')),
    (_t('heLLO'), _t('hello'), _t('HELLO')),
    (
        Text([_s('hello'), _s(' world')]),
        Text([_s('hello'), _s(' world')]), Text([_s('HELLO'), _s(' WORLD')]),
    ),
    (
        Text([_s('HELLO'), _s(' WORLD')]),
        Text([_s('hello'), _s(' world')]), Text([_s('HELLO'), _s(' WORLD')])
    ),
    (
        Text([_s('hello'), _s(' WORLD')]),
        Text([_s('hello'), _s(' world')]), Text([_s('HELLO'), _s(' WORLD')])
    ),
])
def test_text_lower_upper(text: BaseText, lower: BaseText, upper: BaseText):
    assert text_lower(text) == lower
    assert text_upper(text) == upper


@pytest.mark.parametrize("text,result", [
    (Text([]), Text([])),
    (_s(''), _s('')),
    (_s('heLLO'), _s('Hello')),
    (_t('heLLO'), _t('Hello')),
    (Text([_s(''), _t('heLLO')]), Text([_s(''), _t('Hello')])),
    (Text([_s(''), _t('heL'), _s('LO')]), Text([_s(''), _t('Hel'), _s('lo')])),
])
def test_text_capitalize(text: BaseText, result: BaseText):
    assert text_capitalize(text) == result


@pytest.mark.parametrize("text,result", [
    (Text([]), Text([])),
    (_s(''), _s('')),
    (_s('heLLO'), _s('HeLLO')),
    (_t('heLLO'), _t('HeLLO')),
    (Text([_s(''), _t('heLLO')]), Text([_s(''), _t('HeLLO')])),
    (Text([_s(''), _t('heL'), _s('LO')]), Text([_s(''), _t('HeL'), _s('LO')])),
])
def test_text_capfirst(text: BaseText, result: BaseText):
    assert text_capfirst(text) == result


@pytest.mark.parametrize("inputs,outputs,kwargs", [
    ([], [], {}),
    (["one", "two", "three", "four"], ["one", "two", "three", "four"], {}),
    ([], [], dict(sep=", ")),
    (["one"], ["one"], dict(sep=", ")),
    (["one", "two"], ["one", " and ", "two"], dict(sep=", ", sep2=" and ")),
    (
        ["one", "two", "three", "four"],
        ["one", ", ", "two", ", ", "three", ", ", "four"], dict(sep=", ")
    ),
    (
        ["one", "two", "three", "four"],
        ["one", ", ", "two", ", ", "three", ", and ", "four"],
        dict(sep=", ", sep2=" and ", last_sep=", and ")
    ),
    (
        ["one", "two"],
        ["one", " and ", "two"],
        dict(sep=", ", sep2=" and ", other=" and others")
    ),
    (
        ["one", "two", "three", "four"],
        ["one", " and others"],
        dict(sep=", ", sep2=" and ", other=" and others")
    ),
])
def test_list_join(
        inputs: List[str], outputs: List[str], kwargs: Dict[str, str]):
    assert list_join(inputs, **kwargs) == outputs