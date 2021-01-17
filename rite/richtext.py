import dataclasses
from abc import ABC, abstractmethod
from enum import Enum
from typing import Callable, List, Iterable, Any, Optional


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
    def apply_end(self, func: Callable[[str], str]) -> "BaseText":
        """Apply a function to the last string in the text."""
        raise NotImplementedError


@dataclasses.dataclass(frozen=True)
class String(BaseText):
    value: str

    def apply(self, func: Callable[[str], str]) -> BaseText:
        return String(func(self.value))

    def apply_start(self, func: Callable[[str], str]) -> BaseText:
        return self.apply(func)

    def apply_end(self, func: Callable[[str], str]) -> BaseText:
        return self.apply(func)


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

    def apply_end(self, func: Callable[[str], str]) -> BaseText:
        return Tag(self.tag, self.text.apply_end(func))


@dataclasses.dataclass(frozen=True)
class Text(BaseText):
    parts: List[BaseText]

    def apply(self, func: Callable[[str], str]) -> BaseText:
        return Text([part.apply(func) for part in self.parts])

    def apply_start(self, func: Callable[[str], str]) -> BaseText:
        old_part = self.parts[0]
        if isinstance(old_part, Text):
            return Text([old_part.apply_start(func)] + self.parts[1:])
        else:
            return Text([old_part.apply(func)] + self.parts[1:])

    def apply_end(self, func: Callable[[str], str]) -> BaseText:
        old_part = self.parts[-1]
        if isinstance(old_part, Text):
            new_part = old_part.apply_end(func)
        else:
            new_part = old_part.apply(func)
        return Text(self.parts[:-1] + [new_part])


def _join_list(items: List[Any], sep: Any) -> List[Any]:
    return [elem for item in items for elem in (item, sep)][:-1]


def join_text(
        parts: List[BaseText],
        sep: BaseText = String(''),
        sep2: Optional[BaseText] = None,
        last_sep: Optional[BaseText] = None,
        other: Optional[BaseText] = None
        ) -> BaseText:
    if len(parts) <= 1:
        return Text(parts)
    elif len(parts) == 2:
        return Text([parts[0], sep2 if sep2 is not None else sep, parts[1]])
    elif other is None:
        return Text(
            list(_join_list(parts[:-1], sep))
            + [last_sep if last_sep is not None else sep, parts[-1]])
    else:
        return Text([parts[0], other])
