import sys
from typing import TypeVar
if sys.version_info >= (3, 8):
    from typing import Protocol
else:
    from typing_extensions import Protocol

from rite.richtext import Text


RenderType = TypeVar('RenderType', covariant=True)


class RenderProtocol(Protocol[RenderType]):
    def __call__(self, text: Text) -> RenderType:
        pass  # pragma: no cover
