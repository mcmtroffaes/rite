import dataclasses
from abc import ABC, abstractmethod
from enum import Enum
from typing import Callable, Iterator, List


class BaseText(ABC):
    @abstractmethod
    def raw(self) -> Iterator[str]:
        raise NotImplementedError

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

    def raw(self) -> Iterator[str]:
        yield self.value

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
    SUPERSCRIPT = 'sup'
    SUBSCRIPT = 'sub'


@dataclasses.dataclass(frozen=True)
class Tag(BaseText):
    tag: TagType
    text: BaseText

    def raw(self) -> Iterator[str]:
        yield from self.text.raw()

    def apply(self, func: Callable[[str], str]) -> BaseText:
        return Tag(self.tag, self.text.apply(func))

    def apply_start(self, func: Callable[[str], str]) -> BaseText:
        return self.apply(func)

    def apply_end(self, func: Callable[[str], str]) -> BaseText:
        return self.apply(func)


@dataclasses.dataclass(frozen=True)
class Text(BaseText):
    parts: List[BaseText]

    def raw(self) -> Iterator[str]:
        for part in self.parts:
            yield from part.raw()

    def apply(self, func: Callable[[str], str]) -> BaseText:
        return Text([part.apply(func) for part in self.parts])

    def apply_start(self, func: Callable[[str], str]) -> BaseText:
        """Apply a function to the first string in the text."""
        old_part = self.parts[0]
        if isinstance(old_part, Text):
            return Text([old_part.apply_start(func)] + self.parts[1:])
        else:
            return Text([old_part.apply(func)] + self.parts[1:])

    def apply_end(self, func: Callable[[str], str]) -> BaseText:
        """Apply a function to the last string in the text."""
        old_part = self.parts[-1]
        if isinstance(old_part, Text):
            new_part = old_part.apply_end(func)
        else:
            new_part = old_part.apply(func)
        return Text(self.parts[:-1] + [new_part])
