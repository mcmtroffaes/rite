import sys
from typing import TypeVar, Iterable
if sys.version_info >= (3, 8):
    from typing import Protocol
else:
    from typing_extensions import Protocol

from rite.richtext import BaseText


RenderType = TypeVar('RenderType', covariant=True)


class RenderProtocol(Protocol[RenderType]):
    def __call__(self, text: BaseText) -> Iterable[RenderType]:
        pass  # pragma: no cover
