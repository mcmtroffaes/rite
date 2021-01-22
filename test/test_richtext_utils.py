from typing import Callable, List, Dict

import pytest

from rite.richtext import Join, BaseText
from rite.richtext.utils import (
    list_join, text_fmap, text_raw, text_is_empty,
    text_is_lower, text_is_upper, text_lower, text_upper,
    text_capitalize, text_capfirst,
)
from common import _s, _em


@pytest.mark.parametrize(
    "text,func,result_functor_map,result_raw", [
        (
                Join([_s("one "), _em("two"), _s(" three")]),
                lambda x: "*" + x + "*",
                Join([_s("*one *"), _em("*two*"), _s("* three*")]),
                'one two three',
        ),
    ])
def test_text_map(
        text: BaseText, func: Callable[[str], str],
        result_functor_map: BaseText, result_raw: str
):
    assert text_fmap(func, text) == result_functor_map
    assert text_raw(text) == result_raw


@pytest.mark.parametrize("text,is_empty", [
    (_s(''), True),
    (_s('hello'), False),
    (_em(''), True),
    (_em('hello'), False),
    (Join([]), True),
    (Join([_s('')]), True),
    (Join([_s(''), _s('hello')]), False),
])
def test_text_is_empty(text: BaseText, is_empty: bool):
    assert text_is_empty(text) is is_empty


@pytest.mark.parametrize("text,is_lower,is_upper", [
    (_s(''), False, False),
    (_s('hello'), True, False),
    (_s('HELLO'), False, True),
    (_s('heLLO'), False, False),
    (_em('hello'), True, False),
    (_em('HELLO'), False, True),
    (_em('heLLO'), False, False),
    (Join([_s('hello'), _s(' world')]), True, False),
    (Join([_s('HELLO'), _s(' WORLD')]), False, True),
    (Join([_s('hello'), _s(' WORLD')]), False, False),
    (Join([_s('hello'), _s(''), _s(' world')]), True, False),
    (Join([_s('HELLO'), _s(''), _s(' WORLD')]), False, True),
    (Join([_s('hello'), _s(''), _s(' WORLD')]), False, False),
])
def test_text_is_lower_upper(text: BaseText, is_lower: bool, is_upper: bool):
    assert text_is_lower(text) is is_lower
    assert text_is_upper(text) is is_upper


@pytest.mark.parametrize("text,lower,upper", [
    (_s('hello'), _s('hello'), _s('HELLO')),
    (_s('HELLO'), _s('hello'), _s('HELLO')),
    (_s('heLLO'), _s('hello'), _s('HELLO')),
    (_em('hello'), _em('hello'), _em('HELLO')),
    (_em('HELLO'), _em('hello'), _em('HELLO')),
    (_em('heLLO'), _em('hello'), _em('HELLO')),
    (
            Join([_s('hello'), _s(' world')]),
            Join([_s('hello'), _s(' world')]),
            Join([_s('HELLO'), _s(' WORLD')]),
    ),
    (
            Join([_s('HELLO'), _s(' WORLD')]),
            Join([_s('hello'), _s(' world')]),
            Join([_s('HELLO'), _s(' WORLD')]),
    ),
    (
            Join([_s('hello'), _s(' WORLD')]),
            Join([_s('hello'), _s(' world')]),
            Join([_s('HELLO'), _s(' WORLD')]),
    ),
])
def test_text_lower_upper(text: BaseText, lower: BaseText, upper: BaseText):
    assert text_lower(text) == lower
    assert text_upper(text) == upper


@pytest.mark.parametrize("text,result", [
    (Join([]), Join([])),
    (_s(''), _s('')),
    (_s('heLLO'), _s('Hello')),
    (_em('heLLO'), _em('Hello')),
    (Join([_s(''), _em('heLLO')]), Join([_s(''), _em('Hello')])),
    (Join([_s(''), _em('heL'), _s('LO')]),
     Join([_s(''), _em('Hel'), _s('lo')])),
])
def test_text_capitalize(text: BaseText, result: BaseText):
    assert text_capitalize(text) == result


@pytest.mark.parametrize("text,result", [
    (Join([]), Join([])),
    (_s(''), _s('')),
    (_s('heLLO'), _s('HeLLO')),
    (_em('heLLO'), _em('HeLLO')),
    (Join([_s(''), _em('heLLO')]), Join([_s(''), _em('HeLLO')])),
    (Join([_s(''), _em('heL'), _s('LO')]),
     Join([_s(''), _em('HeL'), _s('LO')])),
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
