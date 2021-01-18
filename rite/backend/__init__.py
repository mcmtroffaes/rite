from typing import TypeVar, Iterable
try:
    from typing import Protocol
except ImportError:
    from typing_extensions import Protocol

from rite.richtext import BaseText


RenderType = TypeVar('RenderType', covariant=True)


class RenderProtocol(Protocol[RenderType]):
    def __call__(self, text: BaseText) -> Iterable[RenderType]:
        pass  # pragma: no cover
