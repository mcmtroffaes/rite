import dataclasses
import datetime
try:
    from typing import Protocol
except ImportError:
    from typing_extensions import Protocol

from rite.backend.markdown import render_markdown
from rite.richtext import BaseText, String, TagType, Tag, Text
from rite.style.template import (
    Node, tag, str_, join, capfirst, capitalize, lower, upper
)


# helper function for constructing test cases
def _s(value: str) -> String:
    return String(value)


# helper function for constructing test cases
def _t(value: str) -> Tag:
    return Tag(TagType.CODE, String(value))


def str_data() -> Node[str]:
    """Simple node for constructing templates that take a string as data.
    This node returns the data marked up as code.
    """
    def fmt(data: str) -> BaseText:
        return _t(data)
    return fmt


class NameProtocol(Protocol):
    name: str


def name() -> Node[NameProtocol]:
    def fmt(data: NameProtocol) -> BaseText:
        return String(data.name)
    return fmt


class BirthdayProtocol(Protocol):
    birthday: datetime.date


def birthday(fmt: str) -> Node[BirthdayProtocol]:
    def fmt_(data: BirthdayProtocol) -> BaseText:
        return String(data.birthday.strftime(fmt))
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
    assert template('hello') == Text([_t('hello'), _s(' world')])


def test_protocol() -> None:
    template: Node[PersonProtocol] = join([
        tag(TagType.EMPHASIZE, name()),
        str_(': '),
        tag(TagType.STRONG, birthday("%b %d, %Y"))])
    person1 = Person(
        name='John', birthday=datetime.date(year=1998, month=3, day=7))
    person2 = PersonWithGender(
        name='Mary', birthday=datetime.date(year=1997, month=6, day=22),
        female=True)
    text1 = template(person1)
    text2 = template(person2)
    assert text1 == Text([
        Tag(TagType.EMPHASIZE, _s('John')),
        _s(': '),
        Tag(TagType.STRONG, _s('Mar 07, 1998'))])
    assert text2 == Text([
        Tag(TagType.EMPHASIZE, _s('Mary')),
        _s(': '),
        Tag(TagType.STRONG, _s('Jun 22, 1997'))])
    assert ''.join(render_markdown(text1)) == "*John*: **Mar 07, 1998**"
    assert ''.join(render_markdown(text2)) == "*Mary*: **Jun 22, 1997**"


def test_capfirst():
    template = capfirst(join([str_(''), str_data(), str_(' world')]))
    assert template('hello') == Text([_s(''), _t('Hello'), _s(' world')])


def test_capitalize():
    template = capitalize(join([str_(''), str_data(), str_(' WORLD')]))
    assert template('heLLo') == Text([_s(''), _t('Hello'), _s(' world')])


def test_lower():
    template = lower(join([str_(''), str_data(), str_(' WORLD')]))
    assert template('heLLo') == Text([_s(''), _t('hello'), _s(' world')])


def test_upper():
    template = upper(join([str_(''), str_data(), str_(' WORLD')]))
    assert template('heLLo') == Text([_s(''), _t('HELLO'), _s(' WORLD')])
