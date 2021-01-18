import dataclasses
import datetime
from typing import Protocol

from rite.backend.markdown import render_markdown
from rite.richtext import BaseText, String, TagType, Tag, Text
from rite.style.template import tag, Node, str_, text


def str_data() -> Node[str]:
    """Simple node for constructing templates that take a string as data.
    This node returns the data marked up as code.
    """
    def _(data: str) -> BaseText:
        return Tag(TagType.CODE, String(data))
    return _


class NameProtocol(Protocol):
    name: str


def name() -> Node[NameProtocol]:
    def _(data: NameProtocol) -> BaseText:
        return String(data.name)
    return _


class BirthdayProtocol(Protocol):
    birthday: datetime.date


def birthday(fmt: str) -> Node[BirthdayProtocol]:
    def _(data: BirthdayProtocol) -> BaseText:
        return String(data.birthday.strftime(fmt))
    return _


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
    template: Node[str] = text([str_data(), str_(' world')])
    assert template('hello') == Text([
        Tag(TagType.CODE, String('hello')),
        String(' world'),
    ])


def test_protocol() -> None:
    template: Node[PersonProtocol] = text([
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
        Tag(TagType.EMPHASIZE, String('John')),
        String(': '),
        Tag(TagType.STRONG, String('Mar 07, 1998'))])
    assert text2 == Text([
        Tag(TagType.EMPHASIZE, String('Mary')),
        String(': '),
        Tag(TagType.STRONG, String('Jun 22, 1997'))])
    assert ''.join(render_markdown(text1)) == "*John*: **Mar 07, 1998**"
    assert ''.join(render_markdown(text2)) == "*Mary*: **Jun 22, 1997**"
