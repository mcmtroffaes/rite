from typing import TypeVar, Protocol, Iterable, runtime_checkable
from rite.richtext import BaseText


RenderType = TypeVar('RenderType', covariant=True)


class RenderProtocol(Protocol[RenderType]):
    def __call__(self, text: BaseText) -> Iterable[RenderType]:
        pass
