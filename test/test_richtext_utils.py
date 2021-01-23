from typing import Callable, List, Dict

import pytest

from rite.richtext import Join, Text
from rite.richtext.utils import (
    list_join, text_fmap, text_raw, text_is_empty,
    text_is_lower, text_is_upper, text_lower, text_upper,
    text_capitalize, text_capfirst,
)
from common import _em


@pytest.mark.parametrize(
    "text,func,result_functor_map,result_raw", [
        (
                Join(["one ", _em("two"), " three"]),
                lambda x: "*" + x + "*",
                Join(["*one *", _em("*two*"), "* three*"]),
                'one two three',
        ),
    ])
def test_text_map(
        text: Text, func: Callable[[str], str],
        result_functor_map: Text, result_raw: str
):
    assert text_fmap(func, text) == result_functor_map
    assert text_raw(text) == result_raw


@pytest.mark.parametrize("text,is_empty", [
    ('', True),
    ('hello', False),
    (_em(''), True),
    (_em('hello'), False),
    (Join([]), True),
    (Join(['']), True),
    (Join(['', 'hello']), False),
])
def test_text_is_empty(text: Text, is_empty: bool):
    assert text_is_empty(text) is is_empty


@pytest.mark.parametrize("text,is_lower,is_upper", [
    ('', False, False),
    ('hello', True, False),
    ('HELLO', False, True),
    ('heLLO', False, False),
    (_em('hello'), True, False),
    (_em('HELLO'), False, True),
    (_em('heLLO'), False, False),
    (Join(['hello', ' world']), True, False),
    (Join(['HELLO', ' WORLD']), False, True),
    (Join(['hello', ' WORLD']), False, False),
    (Join(['hello', '', ' world']), True, False),
    (Join(['HELLO', '', ' WORLD']), False, True),
    (Join(['hello', '', ' WORLD']), False, False),
])
def test_text_is_lower_upper(text: Text, is_lower: bool, is_upper: bool):
    assert text_is_lower(text) is is_lower
    assert text_is_upper(text) is is_upper


@pytest.mark.parametrize("text,lower,upper", [
    ('hello', 'hello', 'HELLO'),
    ('HELLO', 'hello', 'HELLO'),
    ('heLLO', 'hello', 'HELLO'),
    (_em('hello'), _em('hello'), _em('HELLO')),
    (_em('HELLO'), _em('hello'), _em('HELLO')),
    (_em('heLLO'), _em('hello'), _em('HELLO')),
    (
            Join(['hello', ' world']),
            Join(['hello', ' world']),
            Join(['HELLO', ' WORLD']),
    ),
    (
            Join(['HELLO', ' WORLD']),
            Join(['hello', ' world']),
            Join(['HELLO', ' WORLD']),
    ),
    (
            Join(['hello', ' WORLD']),
            Join(['hello', ' world']),
            Join(['HELLO', ' WORLD']),
    ),
])
def test_text_lower_upper(text: Text, lower: Text, upper: Text):
    assert text_lower(text) == lower
    assert text_upper(text) == upper


@pytest.mark.parametrize("text,result", [
    (Join([]), Join([])),
    ('', ''),
    ('heLLO', 'Hello'),
    (_em('heLLO'), _em('Hello')),
    (Join(['', _em('heLLO')]), Join(['', _em('Hello')])),
    (Join(['', _em('heL'), 'LO']),
     Join(['', _em('Hel'), 'lo'])),
])
def test_text_capitalize(text: Text, result: Text):
    assert text_capitalize(text) == result


@pytest.mark.parametrize("text,result", [
    (Join([]), Join([])),
    ('', ''),
    ('heLLO', 'HeLLO'),
    (_em('heLLO'), _em('HeLLO')),
    (Join(['', _em('heLLO')]), Join(['', _em('HeLLO')])),
    (Join(['', _em('heL'), 'LO']),
     Join(['', _em('HeL'), 'LO'])),
])
def test_text_capfirst(text: Text, result: Text):
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
