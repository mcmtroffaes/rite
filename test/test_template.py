import dataclasses
import datetime
import sys

from common import _tt, _em, _st

if sys.version_info >= (3, 8):
    from typing import Protocol
else:
    from typing_extensions import Protocol

from rite.richtext import (
    Text, Semantics, Join, FontSizes, FontStyles, FontVariants, FontSize,
    FontStyle, FontVariant, FontWeight
)
from rite.style.template import (
    Node, str_, join, capfirst, capitalize, lower, upper, semantic, font_size,
    font_style, font_variant, font_weight
)


def str_data() -> Node[str]:
    """Simple node for constructing templates that take a string as data.
    This node returns the data marked up as code.
    """
    def fmt(data: str) -> Text:
        return _tt(data)
    return fmt


class NameProtocol(Protocol):
    name: str


def name() -> Node[NameProtocol]:
    def fmt(data: NameProtocol) -> Text:
        return data.name
    return fmt


class BirthdayProtocol(Protocol):
    birthday: datetime.date


def birthday(fmt: str) -> Node[BirthdayProtocol]:
    def fmt_(data: BirthdayProtocol) -> Text:
        return data.birthday.strftime(fmt)
    return fmt_


class PersonProtocol(Protocol):
    name: str
    birthday: datetime.date


@dataclasses.dataclass
class Person:
    name: str
    birthday: datetime.date


@dataclasses.dataclass
class PersonWithGender:
    name: str
    female: bool
    birthday: datetime.date


def test_template() -> None:
    template: Node[str] = join([str_data(), str_(' world')])
    assert template('hello') == Join([_tt('hello'), ' world'])


def test_protocol() -> None:
    template: Node[PersonProtocol] = join([
        semantic(name(), Semantics.EMPHASIS),
        str_(': '),
        semantic(birthday("%b %d, %Y"), Semantics.STRONG)])
    person1 = Person(
        name='John', birthday=datetime.date(year=1998, month=3, day=7))
    person2 = PersonWithGender(
        name='Mary', birthday=datetime.date(year=1997, month=6, day=22),
        female=True)
    text1 = template(person1)
    text2 = template(person2)
    assert text1 == Join([
        _em('John'),
        ': ',
        _st('Mar 07, 1998')])
    assert text2 == Join([
        _em('Mary'),
        ': ',
        _st('Jun 22, 1997')])


def test_capfirst() -> None:
    template: Node[str] = \
        capfirst(join([str_(''), str_data(), str_(' world')]))
    assert template('hello') == Join(['', _tt('Hello'), ' world'])


def test_capitalize() -> None:
    template: Node[str] = \
        capitalize(join([str_(''), str_data(), str_(' WORLD')]))
    assert template('heLLo') == Join(['', _tt('Hello'), ' world'])


def test_lower() -> None:
    template: Node[str] = lower(join([str_(''), str_data(), str_(' WORLD')]))
    assert template('heLLo') == Join(['', _tt('hello'), ' world'])


def test_upper() -> None:
    template: Node[str] = upper(join([str_(''), str_data(), str_(' WORLD')]))
    assert template('heLLo') == Join(['', _tt('HELLO'), ' WORLD'])


def test_style() -> None:
    template: Node[str] = join([
        font_size(str_('my'), FontSizes.SMALL),
        str_(' '), font_style(str_('name'), FontStyles.ITALIC),
        str_(' '), font_variant(str_('is'), FontVariants.SMALL_CAPS),
        str_(' '), font_weight(str_data(), 900),
    ])
    assert template('merlin') == Join([
        FontSize('my', FontSizes.SMALL),
        ' ', FontStyle('name', FontStyles.ITALIC),
        ' ', FontVariant('is', FontVariants.SMALL_CAPS),
        ' ', FontWeight(_tt('merlin'), 900),
    ])
