import dataclasses
from abc import ABC, abstractmethod
from enum import Enum
from typing import Callable, List, Any, Optional, TypeVar, Iterable

T = TypeVar('T')


class BaseText(ABC):
    @abstractmethod
    def apply(self, func: Callable[[str], str]) -> "BaseText":
        """Apply a function to every string in the text."""
        raise NotImplementedError

    @abstractmethod
    def apply_start(self, func: Callable[[str], str]) -> "BaseText":
        """Apply a function to the first string in the text."""
        raise NotImplementedError

    @abstractmethod
    def apply_iter(self, func: Callable[[str], T]) -> Iterable[T]:
        """Apply a function to every string in the text."""
        raise NotImplementedError


@dataclasses.dataclass(frozen=True)
class String(BaseText):
    value: str

    def apply(self, func: Callable[[str], str]) -> BaseText:
        return String(func(self.value))

    def apply_start(self, func: Callable[[str], str]) -> BaseText:
        return self.apply(func)

    def apply_iter(self, func: Callable[[str], T]) -> Iterable[T]:
        yield func(self.value)


class TagType(Enum):
    """Rich text tags. Values are html tags."""
    EMPHASIZE = 'em'
    STRONG = 'strong'
    CODE = 'code'
    SUPERSCRIPT = 'sup'
    SUBSCRIPT = 'sub'


@dataclasses.dataclass(frozen=True)
class Tag(BaseText):
    tag: TagType
    text: BaseText

    def apply(self, func: Callable[[str], str]) -> BaseText:
        return Tag(self.tag, self.text.apply(func))

    def apply_start(self, func: Callable[[str], str]) -> BaseText:
        return Tag(self.tag, self.text.apply_start(func))

    def apply_iter(self, func: Callable[[str], T]) -> Iterable[T]:
        yield from self.text.apply_iter(func)


@dataclasses.dataclass(frozen=True)
class Text(BaseText):
    parts: List[BaseText]

    def apply(self, func: Callable[[str], str]) -> BaseText:
        return Text([part.apply(func) for part in self.parts])

    def apply_start(self, func: Callable[[str], str]) -> BaseText:
        tail = (part for part in self.parts)
        head = next(tail, None)
        if head is None:
            return self
        elif isinstance(head, Text):
            return Text([head.apply_start(func)] + list(tail))
        else:
            return Text([head.apply(func)] + list(tail))

    def apply_iter(self, func: Callable[[str], T]) -> Iterable[T]:
        for part in self.parts:
            yield from part.apply_iter(func)


@dataclasses.dataclass(frozen=True)
class Protected(Text):

    def apply(self, func: Callable[[str], str]) -> BaseText:
        return self

    def apply_start(self, func: Callable[[str], str]) -> BaseText:
        return self


def is_empty(text: BaseText) -> bool:
    return not any(text.apply_iter(bool))


def is_upper(text: BaseText) -> bool:
    return all(text.apply_iter(str.isupper))


def is_lower(text: BaseText) -> bool:
    return all(text.apply_iter(str.islower))


def upper(text: BaseText) -> BaseText:
    return text.apply(str.upper)


def lower(text: BaseText) -> BaseText:
    return text.apply(str.lower)


def capitalize(text: BaseText) -> BaseText:
    return text.apply(str.lower).apply_start(str.capitalize)


def join_list(
        sep: BaseText,
        parts: List[BaseText],
        sep2: Optional[BaseText] = None,
        last_sep: Optional[BaseText] = None,
        other: Optional[BaseText] = None
        ) -> List[BaseText]:
    if not parts:
        return []
    elif len(parts) == 1:
        return [parts[0]]
    elif len(parts) == 2:
        return [parts[0], sep2 if sep2 is not None else sep, parts[1]]
    elif other is None:
        _last_sep: BaseText = last_sep if last_sep is not None else sep
        first = [text for part in parts[:-2] for text in [part, sep]]
        last = [parts[-2], _last_sep, parts[-1]]
        return first + last
    else:
        return [parts[0], other]
